extends GutTest

const ENEMY = preload("res://enemy.tscn")
const LEVEL = preload("res://main.tscn")


func after_each() -> void:
	get_tree().paused = false


func test_saved_children() -> void:
	var enemy = ENEMY.instantiate()
	add_child_autofree(enemy)
	assert_true(enemy.has_node("Body"))
	assert_true(enemy.has_node("Health"))
	assert_true(enemy.has_node("Pulse"))


func test_inspector_tuning_affects_damage() -> void:
	var enemy = ENEMY.instantiate()
	enemy.health = 5
	add_child_autofree(enemy)
	watch_signals(enemy)
	for i in range(4):
		enemy.take_damage(1)
	assert_eq(enemy.state.health, 1)
	assert_signal_not_emitted(enemy, "defeated")
	enemy.take_damage(1)
	enemy.take_damage(1)
	assert_eq(enemy.state.health, 0)
	assert_signal_emit_count(enemy, "defeated", 1)


func test_mutable_state_is_instance_owned() -> void:
	var first = ENEMY.instantiate()
	var second = ENEMY.instantiate()
	add_child_autofree(first)
	add_child_autofree(second)
	first.take_damage(1)
	assert_ne(first.state, second.state)
	assert_eq(first.state.health, 2)
	assert_eq(second.state.health, 3)
	assert_eq(first.state.counters[0], 1)
	assert_eq(second.state.counters[0], 0)


func test_definition_is_intentionally_shared() -> void:
	var first = ENEMY.instantiate()
	var second = ENEMY.instantiate()
	add_child_autofree(first)
	add_child_autofree(second)
	assert_same(first.definition, second.definition)


func test_remove_reenter_does_not_duplicate_callbacks() -> void:
	var enemy = ENEMY.instantiate()
	add_child_autofree(enemy)
	remove_child(enemy)
	add_child(enemy)
	enemy.pulse.timeout.emit()
	assert_eq(enemy.ready_count, 1)
	assert_eq(enemy.pulse_count, 1)


func test_teardown_settles() -> void:
	var enemy = ENEMY.instantiate()
	add_child(enemy)
	var reference = weakref(enemy)
	enemy.pulse.start(1.0)
	enemy.queue_free()
	await get_tree().process_frame
	assert_null(reference.get_ref())


func test_pause_resume_does_not_hit() -> void:
	var level = LEVEL.instantiate()
	add_child_autofree(level)
	level.set_paused(true)
	assert_true(get_tree().paused)
	level.get_node("HUD/PausePanel/Resume").pressed.emit()
	assert_false(get_tree().paused)
	assert_eq(level.hits, 0)
	assert_eq(level.left.state.health, 3)


func test_native_save_ownership() -> void:
	var root = Node2D.new()
	var child = Node2D.new()
	child.name = "OwnedChild"
	root.add_child(child)
	child.owner = root
	var packed = PackedScene.new()
	assert_eq(packed.pack(root), OK)
	var restored = packed.instantiate()
	assert_true(restored.has_node("OwnedChild"))
	root.free()
	restored.free()


func _send_physical_key(key: Key, pressed: bool) -> void:
	var event = InputEventKey.new()
	event.physical_keycode = key
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()


func test_physical_bindings_reach_expected_enemy() -> void:
	# Fixed expected keys are independent of the configured InputMap values.
	for key in [KEY_LEFT, KEY_A, KEY_RIGHT, KEY_D]:
		var level = LEVEL.instantiate()
		add_child(level)
		var focused = get_viewport().gui_get_focus_owner()
		if focused:
			focused.release_focus()
		_send_physical_key(key, true)
		await get_tree().process_frame
		_send_physical_key(key, false)
		await get_tree().process_frame
		var hits_left: bool = key == KEY_LEFT or key == KEY_A
		assert_eq(level.left.state.health, 2 if hits_left else 3, "left health for key %s" % key)
		assert_eq(level.right.state.health, 3 if hits_left else 2, "right health for key %s" % key)
		assert_eq(level.hits, 1, "one gameplay hit for key %s" % key)
		assert_eq(level.hits_label.text, "Gameplay hits: 1")
		assert_false(Input.is_action_pressed("hit_left"), "left action released")
		assert_false(Input.is_action_pressed("hit_right"), "right action released")
		level.queue_free()
		await get_tree().process_frame


func test_physical_pause_keys_reach_scene() -> void:
	for key in [KEY_P, KEY_ESCAPE]:
		var level = LEVEL.instantiate()
		add_child(level)
		_send_physical_key(key, true)
		await get_tree().process_frame
		_send_physical_key(key, false)
		await get_tree().process_frame
		assert_true(get_tree().paused, "physical pause key %s" % key)
		assert_true(level.pause_panel.visible)
		assert_eq(level.hits, 0)
		level.set_paused(false)
		level.queue_free()
		await get_tree().process_frame

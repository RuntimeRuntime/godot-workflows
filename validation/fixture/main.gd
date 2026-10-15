extends Node2D

var hits: int = 0

@onready var left: Node2D = $Left
@onready var right: Node2D = $Right
@onready var pause_panel: Panel = $HUD/PausePanel
@onready var hits_label: Label = $HUD/Hits


func _ready() -> void:
	$HUD/HitLeft.pressed.connect(hit_left)
	$HUD/HitRight.pressed.connect(hit_right)
	$HUD/Pause.pressed.connect(func() -> void: set_paused(true))
	$HUD/PausePanel/Resume.pressed.connect(func() -> void: set_paused(false))


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		set_paused(not get_tree().paused)
		get_viewport().set_input_as_handled()
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if not get_tree().paused:
			hit_left()


func hit_left() -> void:
	if not get_tree().paused:
		left.take_damage(1)
		hits += 1
		_update_hits()


func hit_right() -> void:
	if not get_tree().paused:
		right.take_damage(1)
		hits += 1
		_update_hits()


func set_paused(value: bool) -> void:
	get_tree().paused = value
	pause_panel.visible = value
	if value:
		$HUD/PausePanel/Resume.grab_focus()


func _update_hits() -> void:
	hits_label.text = "Gameplay hits: %d" % hits

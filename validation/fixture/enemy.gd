extends Node2D

signal defeated

@export var health: int = 3
@export var state: WorkflowActorState
@export var definition: WorkflowEnemyDefinition

var ready_count: int = 0
var pulse_count: int = 0
var is_defeated: bool = false

@onready var health_label: Label = $Health
@onready var pulse: Timer = $Pulse


func _ready() -> void:
	ready_count += 1
	state.health = health
	pulse.timeout.connect(_on_pulse)
	_update_label()


func take_damage(amount: int) -> void:
	if is_defeated:
		return
	state.health = maxi(0, state.health - amount)
	state.counters[0] += 1
	if state.health == 0:
		is_defeated = true
		defeated.emit()
	_update_label()


func _on_pulse() -> void:
	pulse_count += 1


func _exit_tree() -> void:
	pulse.stop()


func _update_label() -> void:
	health_label.text = "DEFEATED" if is_defeated else "Health: %d" % state.health
	$Body.modulate = Color(0.35, 0.4, 0.5) if is_defeated else Color.WHITE

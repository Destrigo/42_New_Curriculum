print("=== Circular Curse Breaking ===")

import alchemy.grimoire as gr

print("Testing ingredient validation:")
print('validate_ingredients("fire air"):', gr.validate_ingredients("fire air"))
print('validate_ingredients("dragon scales"):', gr.validate_ingredients("dragon scales"))

print("\nTesting spell recording with validation:")
print(
    'record_spell("Fireball", "fire air"):',
    gr.record_spell("Fireball", "fire air")
)
print(
    'record_spell("Dark Magic", "shadow"):',
    gr.record_spell("Dark Magic", "shadow")
)

print("\nTesting late import technique:")
print(
    'record_spell("Lightning", "air"):',
    gr.record_spell("Lightning", "air")
)

print("\nCircular dependency curse avoided using late imports!")
print("All spells processed safely!")

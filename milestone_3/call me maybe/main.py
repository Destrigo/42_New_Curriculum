from runtime import init_context, load_function_defs, load_prompts
from fsm import FSMState

ctx = init_context()

print(ctx.state)
ctx.state = FSMState.OPEN_OBJECT
print(ctx.state)
ctx.state = FSMState.EXPECT_FUNCTION_KEY
print(ctx.state)
functions = load_function_defs("data/functions.json")
prompts = load_prompts("data/prompts.json")

print(functions.keys())
print(prompts[0])

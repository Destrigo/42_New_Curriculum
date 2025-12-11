from .GameEngine import GameEngine
from .FantasyCardFactory import FantasyCardFactory
from .AggressiveStrategy import AggressiveStrategy

def main():
    print("=== DataDeck Game Engine ===")
    factory = FantasyCardFactory()
    strategy = AggressiveStrategy()
    
    engine = GameEngine()
    engine.configure_engine(factory, strategy)
    
    print("Configuring Fantasy Card Game...")
    print(f"Factory: {factory.__class__.__name__}")
    print(f"Strategy: {strategy.get_strategy_name()}")
    print(f"Available types: {factory.get_supported_types()}")
    
    print("Simulating aggressive turn...")
    report = engine.simulate_turn()
    print("Game Report:")
    print(report)
    print("Abstract Factory + Strategy Pattern: Maximum flexibility achieved!")

if __name__ == "__main__":
    main()

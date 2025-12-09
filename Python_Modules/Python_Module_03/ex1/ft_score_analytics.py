import sys

if __name__ == "__main__":
    """first try"""
    print("=== Player Score Analytics ===")
    arg = len(sys.argv)
    if arg == 1:
        print("No scores provided. Usage: pythonr3 ft_score_analytics.py <score1> <score2> ...")
    else:
        score_list = []
        i = 1
        while i < arg:
            try:
                score_list += [int(sys.argv[i])]
            except ValueError:
                print(f"ATTENTION! {sys.argv[i]} is a non-int score!")
                print("")
            i += 1
        print(f"Scores processed: {score_list}")
        print(f"Total players: {arg - 1}")
        print(f"Total score: {sum(score_list)}")
        print(f"Average score: {int(sum(score_list) / len(score_list))}")
        print(f"High score: {max(score_list)}")
        print(f"Low score: {min(score_list)}")
        print(f"Score range: {max(score_list) - min(score_list)}")
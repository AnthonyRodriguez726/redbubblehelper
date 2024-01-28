from search_info import rewrite_prompt

def test_rewrite_prompt():
    test_prompt = "Create an attack on titan design"
    rewritten_prompt = rewrite_prompt(test_prompt)
    print("Original Prompt:", test_prompt)
    print("Rewritten Prompt:", rewritten_prompt)

if __name__ == "__main__":
    test_rewrite_prompt()
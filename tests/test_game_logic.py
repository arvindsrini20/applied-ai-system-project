from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"

def test_too_high_returns_correct_status():
    # Bug fix: when guess is too high, status should be "Too High" not "Too Low"
    assert check_guess(80, 50) == "Too High"

def test_too_low_returns_correct_status():
    # Bug fix: when guess is too low, status should be "Too Low" not "Too High"
    assert check_guess(20, 50) == "Too Low"

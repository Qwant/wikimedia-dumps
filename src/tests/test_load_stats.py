from load_stats import load_file, load_stats


def test_unexisting_file():
    # the output dictionary should contain an empty field for each language
    stats = load_file('this_is_a_fake_file.csv.gz')
    assert all(not lang for lang in stats.values())

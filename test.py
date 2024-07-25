def test_country_in_flags(country, my_flags):
    return country in my_flags.get(country, "")


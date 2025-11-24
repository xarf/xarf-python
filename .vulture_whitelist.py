# Vulture whitelist for intentionally unused code
# https://github.com/jendrikseipp/vulture

# Pydantic validators require 'cls' parameter even if unused
_.cls  # unused variable (validators)

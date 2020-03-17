"""Integration with https://github.com/ARMmbed/mbed-tools."""
import pdoc

config_variables = pdoc.Module("mbed_targets.config").variables()

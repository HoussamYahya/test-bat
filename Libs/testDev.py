import NI_8012
import canStatistics

# Start the power supply
test = NI_8012.virtualBench()
test.ps_configure_output(NI_8012.PS_25V_POS, 13.0, 0.1)
test.ps_configure_output(NI_8012.PS_25V_NEG, -13.0, 0.1)
test.ps_enable()

canStats = canStatistics.canStatistics(bitrate=250000)
rx_stats = canStats.get_period(0x18ff4ff4, 10, extended=True)
print(rx_stats)

test.release()

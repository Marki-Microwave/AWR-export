import MWO_Parser as MWO
from data_handle import data_handler
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D

from cycler import cycler

parser = MWO.APFileParser(r"Y:\HFSS_Simulation_Archives\Peter\Amplifier\PE15 LNA\MWO\Verification\1018.txt")
df = parser.get_dataframe()
data_dict = parser.to_dict()

print(df.columns)
print("Original column for 'DB(|S(1,2)|)':", parser.get_original_column_name("DB(|S(1,2)|)"))
path = r"S:\Engineering\Test Data\Amplifiers\PE15-Gen9\test_structures\6_16_25_linearity\plots"
savepath = r"S:\Engineering\Test Data\Amplifiers\PE15-Gen9\test_structures\6_16_25_linearity\plots"
Data = data_handler(path, savepath)
NF_deembed = Data.data[0][1][:,2]/2 # Probe cal insertion loss

path = r"S:\Engineering\Test Data\Amplifiers\PE15-Gen9\test_structures\6_16_25_linearity\plots\NF"
DataNF_meas = data_handler(path, savepath)


path = r"S:\Engineering\Test Data\Amplifiers\PE15-Gen9\test_structures\6_16_25_linearity\plots\10708_1018"
savepath = r"S:\Engineering\Test Data\Amplifiers\PE15-Gen9\test_structures\6_16_25_linearity\plots"

mpl.rcParams['axes.prop_cycle'] = cycler(color=['k', 'k', 'b', 'r','r'], ls=['-', 'dotted', '-', '--','--'])
mpl.rcParams['axes.prop_cycle'] = cycler(color=['b', 'b', 'm', 'm', 'brown', 'brown']) + \
                                  cycler(ls=['-', '--', '-', '--', '-', '--'])

font = {'size': 16}
mpl.rc('font', **font)
plt.rcParams['figure.figsize'] = [10, 5.05]
plt.rcParams['font.family'] = "Calibri"

legend_elements = [
    Line2D([0], [0], color='b', lw=2, label='S11 (dB)'),
    Line2D([0], [0], color='m', lw=2, label='S21 (dB)'),
    Line2D([0], [0], color='brown', lw=2, label='S22 (dB)'),
    Line2D([0], [0], color='k', lw=2, linestyle='-', label='Measured (Solid)'),
    Line2D([0], [0], color='k', lw=2, linestyle='--', label='Simulated (Dashed)'),
]
legend_elements_NF = [
    Line2D([0], [0], color='k', lw=2, linestyle='-', label='Measured (Solid)'),
    Line2D([0], [0], color='k', lw=2, linestyle='--', label='Simulated (Dashed)'),
]


Data = data_handler(path, savepath)
f1 = (Data.data[0][5][:,0]/1e9)
S11_meas = Data.data[0][5][:,1]
S12_meas = Data.data[0][5][:,2]
S21_meas = Data.data[0][5][:,3]
S22_meas = Data.data[0][5][:,4]
f_NF = DataNF_meas.data[0][1][:,0]/1e9
NF_meas = DataNF_meas.data[2][1][:,1] + NF_deembed
stepx = 2
stepy = 10
xlim = [0,26.01]
ylim = [-30,50.01]

fig, ax = plt.subplots()
ax.set_title("LNA Test Structure 10 - 18 GHz")
ax.plot(f1, S11_meas)
ax.plot(df['Frequency (GHz)'], df['DB(|S(1,1)|)'])
ax.plot(f1, S21_meas)
ax.plot(df['Frequency (GHz)'], df['DB(|S(2,1)|)'])
ax.plot(f1, S22_meas)
ax.plot(df['Frequency (GHz)'], df['DB(|S(2,2)|)'])
ax.set_ylim(ylim)
ax.set_xlim(xlim)
ax.xaxis.set_major_locator(MultipleLocator(stepx))
ax.yaxis.set_major_locator(MultipleLocator(stepy))
ax.set_xlabel("Frequency (GHz)")
ax.legend(handles=legend_elements, loc='upper right')
ax.grid()
plt.show()

plt.rcParams['figure.figsize'] = [5, 5.05]

fig, ax = plt.subplots()
print(NF_deembed)

ax.plot(f_NF, NF_meas,color="k")
ax.plot(df['Frequency (GHz)'], df['DB(NF(2,1))'],color="k")
ax.set_xlabel("Frequency (GHz)")
ax.set_title("NF (dB)")
ax.set_xlim(xlim)
ax.set_ylim([0,5])
ax.legend(handles=legend_elements_NF, loc='upper right')
ax.grid()
ax.xaxis.set_major_locator(MultipleLocator(stepx))
ax.yaxis.set_major_locator(MultipleLocator(1))
plt.show()
mpl.rcParams['axes.prop_cycle'] = cycler(color=['k', 'k', 'b', 'r','r'], ls=['-', 'dotted', '-', '--','--'])
plt.rcParams['figure.figsize'] = [7, 7]
legend_bias = ["3V 12mA", "4V 18mA"]
Data.plot_data(0,3,2,title="OIP3 (dBm)",xlim=xlim,ylim = [0,30.01],legend=legend_bias,xtick=2,ytick=5)
Data.plot_data(0,2,4,title="P1dB Output (dBm)",xlim=xlim,ylim = [-10,15.01],legend=legend_bias,xtick=2,ytick=5)


"""
data_handle.py

Contains Object: data_handler
    Reads and manages data from folders containing csv data files from Keysight VNAs
"""
import os
import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

class data_handler:
    def __init__(self, data_path, save_path):
        self.data_path = data_path
        self.save_path = save_path
        # Get list of csv files in folder
        self.csv_list = self.get_csv_list()
        print(self.csv_list)
        # Trace Names
        self.traces = self.get_trace_names()
        # For each file get data
        self.data, self.data_labels = self.get_csv_data()

    def get_csv_list(self):
        dir_list = os.listdir(self.data_path)
        csv_list = []
        for file in dir_list:
            if file.endswith(".csv"):
                csv_list.append(file)
        return csv_list

    def get_csv_data(self):
        data = []
        data_labels = []
        info = []
        for f_csv in self.csv_list:
            path = os.path.join(self.data_path, f_csv)
            with open(path, newline='') as csvfile:
                # full csv contents
                file_dump = csvfile.read()
                # splitting by Channel
                file_dump = file_dump.split("END")
                file_dump = file_dump[:len(file_dump) - 1]
                # print(path)
                # print(file_dump[0].split(("\n")))
                file_info = file_dump[0].split("\n")[0:4]

                file_info = "\n".join(file_info)
                info.append(file_info)

                data_f = []
                labels_c = []
                # print("chan cnt"+ str(len(file_dump)))
                for channel in file_dump:
                    channel = channel[channel.find("DATA") + 6:len(channel) - 2]
                    channel = channel.split("\n")
                    # print(channel)
                    labels_c.append(channel[0].split(","))
                    # print(labels_c)
                    data_c = []
                    # print(channel)
                    for row in channel[1::]:
                        data_c.append([float(x) for x in row.split(",")])
                    data_f.append(np.array(data_c))
                data.append(data_f)
                data_labels.append(labels_c)
        return data, data_labels

    def average_in_range(self, label_ind_x, label_ind_y, chan_ind, f_range):
        for i in range(len(self.data)):
            x_dat = (self.data[i][chan_ind][:, label_ind_x])
            x_dat = np.divide(x_dat, 1e9)
            y_dat = (self.data[i][chan_ind][:, label_ind_y])

            # x_dat_t = [i for i in x_dat if (f_range[0] <= i <= f_range[1])]
            # print((np.where(x_dat>=f_range[0]))[0])
            trim = [(np.where(x_dat >= f_range[0]))[0].min(), (np.where(x_dat <= f_range[1]))[0].max()]
            # print(trim)
            # trim = [x_dat.index(x_dat_t[0]), len(x_dat_t)-1]
            y_dat_t = y_dat[trim[0]:trim[1]]
            x_dat_t = x_dat[trim[0]:trim[1]]

            # print(len(y_dat_t), len(x_dat_t))
            avg = np.mean(y_dat_t)
            # print(i, self.traces[i])
            # print(self.traces[i] ,self.data_labels[i][chan_ind][label_ind_y] ,avg)
            #print(self.traces[i])
            print(self.data_labels[i][chan_ind][label_ind_y])
            print('     avg= ', avg)
        # print(self.data_labels[1][chan_ind])
    # Running average smoother n points up n points down from center
    # Data = [x, y]
    # Smooths y and returns trimmed x
    def smooth_data(self, data, n):
        y = []
        for i, dat in enumerate(data[1]):
            if (i > n-1) and (i < len(data[0]) - n - 1):
                y.append(sum(data[1][(i-n):(i+n)]/len(data[1][(i-n):(i+n)])))
        x = data[0][n:]
        x = x[:(len(data[0])-n)]
        return x,y

    def plot_data(self, label_ind_x, label_ind_y, chan_ind, title=None, xlim=None, ylim=None,
                  xtick=None, ytick=None, legend=None, logscale=False, avg=[False, [0, 0]], ret_ax=False, pass_ax=False,
                  ax_fig=None, fig_res = (20, 12), trim = False, trim_low = False, Mhz = False, smooth = False, lesspoints = False, remove_fpoints = False):
        data_x = []
        data_y = []
        plt.figure(figsize=fig_res)
        if avg[0]:
            self.average_in_range(label_ind_x, label_ind_y, chan_ind, avg[1])
        if not pass_ax:
            fig, ax = plt.subplots()
        else:
            ax = ax_fig[0]
            fig = ax_fig[1]



        ax.grid(True, which="both")
        if logscale:
            plt.xscale("log")
        # for file_d in self.data:
        #     data_x.append(file_d[chan_ind][:, label_ind_x])
        #     data_y.append(file_d[chan_ind][:, label_ind_y])
        for i in range(len(self.data)):
            x_dat = (self.data[i][chan_ind][:, label_ind_x])
            y_dat = (self.data[i][chan_ind][:, label_ind_y])

            if not (logscale or Mhz):
                x_dat = np.divide(x_dat, 1e9)
            if Mhz:
                x_dat = np.divide(x_dat, 1e6)
            # Typically for removing NF spikes from plots due to EMI (Wifi)
            if remove_fpoints:
                Find = True
                xi = 0
                xi_low = None
                while Find:
                    if (x_dat[xi] >= remove_fpoints[0]) and xi_low is None:
                        xi_low = xi
                    if x_dat[xi] >= remove_fpoints[1]:
                        xi_high = xi
                        Find = False
                    xi +=1
                x_dat = np.concatenate((x_dat[0:xi_low],x_dat[xi_high:]))
                y_dat = np.concatenate((y_dat[0:xi_low],y_dat[xi_high:]))

            if lesspoints:
                x_temp = []
                y_temp = []
                for xi,x in enumerate(x_dat):
                    if xi % lesspoints == 0:

                        x_temp.append(x)
                        y_temp.append(y_dat[xi])
                x_dat = x_temp
                y_dat = y_temp
            if trim:
                for xi, x in enumerate(x_dat):
                    if x >= trim[i]:
                        xi_0 = xi
                        break
                x_dat = x_dat[0:xi_0]
                y_dat = y_dat[0:xi_0]

            if trim_low:
                for xi, x in enumerate(x_dat):
                    if x >= trim_low[i]:
                        xi_0 = xi
                        break
                x_dat = x_dat[xi_0:]
                y_dat = y_dat[xi_0:]
            #print("i="+str(i))
            #print("chan_ind"+str(chan_ind))
            #print("label_ind_y"+str(label_ind_y))

            if smooth is False:
                ax.plot(x_dat, y_dat, label=self.traces[i])
            else:
                print("smoothing")
                x_dat, y_dat = self.smooth_data([x_dat,y_dat], smooth)
                ax.plot(x_dat, y_dat, label=self.traces[i])

        # print(self.data_labels)

        if title is None:
            ax.set_title(self.data_labels[0][chan_ind][label_ind_y])
            filename = self.data_labels[0][chan_ind][label_ind_y] + ".png"
        else:
            ax.set_title(title, weight ='bold')
            filename = title + ".png"

        if xlim is not None:
            ax.set_xlim(xlim)
            if xtick is not None:
                ax.xaxis.set_ticks(np.arange(xlim[0], xlim[1], xtick))

        if ylim is not None:
            ax.set_ylim(ylim)
            if ytick is not None:
                ax.yaxis.set_ticks(np.arange(ylim[0], ylim[1], ytick))
        if not (logscale or Mhz):
            ax.set_xlabel("Frequency (GHz)",weight= 'bold')
        elif Mhz:
            ax.set_xlabel("Freq (MHz)")
        else:
            ax.set_xlabel("Freq(Hz)")

        if legend is None:
            ax.legend()
        elif legend == "off":
            print(" ")
        else:
            ax.legend(legend)

        fig.savefig(os.path.join(self.save_path, filename), dpi=800, bbox_inches='tight')
        # plt.show()
        if ret_ax:
            return ax, fig

    def overplot(self, label_x_y_chan_list, title=None, xlim=None, ylim=None,
                  xtick=None, ytick=None, legend=[]):
        fig, ax = plt.subplots()
        for item in label_x_y_chan_list:
            ax, fig = self.plot_data(item[0], item[1], item[2], ret_ax=True, pass_ax=True, ax_fig=[ax, fig])
        ax.set_title(title)
        if xlim is not None:
            ax.set_xlim(xlim)
            if xtick is not None:
                ax.xaxis.set_ticks(np.arange(xlim[0], xlim[1], xtick))

        if ylim is not None:
            ax.set_ylim(ylim)
            if ytick is not None:
                ax.yaxis.set_ticks(np.arange(ylim[0], ylim[1], ytick))
        ax.legend(legend)
        fig.savefig(os.path.join(self.save_path, title), dpi=1200)

    def get_trace_names(self):
        trace_names = []
        for filename in self.csv_list:
            # index = filename.find("V")
            # index_end = filename.find("mA")
            # trace_names.append(filename[index - 1:index_end + 2])
            index_end = filename.find(".csv")
            trace_names.append(filename[0:index_end])
        return trace_names

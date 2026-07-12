import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcol

color_dict = mcol.TABLEAU_COLORS


def lin2db(x):
    return 10*np.log10(x)


def db2lin(x):
    return 10**(x/10)


class ADC:
    fs_step = 2.75625e3
    
    def __init__(self, n_bit):
        self.n_bit = n_bit

    def snr(self):
        return self.n_bit*6

class BSC:
    
    def __init__(self, error_probability):
        self.error_probability = error_probability


    def snr(self):
        snr_lin = 1/(4*self.error_probability);

        snr_db = 10*np.log10(snr_lin)
        return snr_db


class PCM:

    def __init__(self):
        pass

    
def exercise_1():
    n_bit = np.array( [2, 3, 4, 6, 8, 10, 12, 14, 16], dtype='int64')


    # Quantization SNR
    adc = ADC(n_bit)
    quant_snr = adc.snr()

    plt.figure(1)

    plt.plot(n_bit, quant_snr, 'ro-', label='Quantization SNR');
    plt.xlabel('Number of bits')
    plt.ylabel('SNR [dB]')

    print(quant_snr)
    plt.title('Quantization SNR vs. n_bit')
    plt.grid(True)
    plt.savefig("quant_snr.png")

    # BSC SNR
    pe_values = np.logspace(-12, 0, num=1000)
    bsc = BSC(pe_values)

    plt.figure(2)
    plt.plot(pe_values, bsc.snr(), 'b-', label='BSC SNR');
    plt.xscale('log')
    plt.xlabel('Bit Error Probability(Pe) log scale')

    plt.ylabel('SNR [dB]')
    plt.title('BSC SNR vs. Bit Error Probability')
    plt.grid(True)
    plt.savefig("bsc_snr.png")



def exercise_2():
    


def exercise_3():
    pass



if __name__ == "__main__":
    print("Laboratory 3 - ADC-BSC")
    
    exercise_1()
    exercise_2()
    exercise_3()

    


    
    
    
    
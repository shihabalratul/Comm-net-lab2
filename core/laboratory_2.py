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
        snr_q_lin = 2**(2*self.n_bit)
        return lin2db(snr_q_lin)

class BSC:
    
    def __init__(self, error_probability):
        self.error_probability = error_probability


    def snr(self):
        
        snr_lin = 1/(4*self.error_probability)

        snr_db = lin2db(snr_lin)
       
        return snr_db


class PCM:
    def __init__(self, n_bit, error_probability, analog_bandwidth=1.0):
        self.analog_bandwidth = analog_bandwidth
        self.adc = ADC(n_bit)
        self.bsc = BSC(error_probability)     
        self.M = 2**n_bit   

    def snr(self):
        snr_q_db = self.adc.snr()
        snr_bsc_db = self.bsc.snr()

        snr_q_lin = db2lin(snr_q_db)
        snr_bsc_lin = db2lin(snr_bsc_db)

        snr_total_lin = 1/(1/snr_q_lin + 1/snr_bsc_lin)

        snr_total_db = lin2db(snr_total_lin)
        return snr_total_db

    def critical_pe(self):
        M = self.M
        return 1 / (4 * (M**2 - 1))


    
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
    n_bit = np.array([2, 4, 8, 16], dtype='int64')
    pe_values = np.logspace(-12, 0, num=1000)

    colors = ['blue', 'orange', 'green', 'red']

    plt.figure(3, figsize=(10, 6))

    plt.xscale('log')
    for i, n in enumerate(n_bit):
        
        pcm = PCM(n, pe_values)
        snr_values = pcm.snr()

        plt.plot(pe_values, snr_values, color=colors[i], label=f'n bit={n}')

        adc = ADC(n)
        snr_q_db = adc.snr()
        plt.axhline(y=snr_q_db, color=colors[i], linestyle='--')

        p_th = pcm.critical_pe()
        plt.axvline(x=p_th, color=colors[i], linestyle=':')
    
    plt.xlabel('Bit Error Probability (Pe) [log scale]')
    plt.ylabel('Overall SNR [dB]')
    plt.title('Overall SNR vs. Bit Error Probability for different n_bit')
    plt.grid(True)
    plt.legend(loc='upper right', fontsize='small')
    plt.tight_layout()

    plt.savefig("PCM_ex_2.png")


def exercise_3():
    pass



if __name__ == "__main__":
    print("Laboratory 3 - ADC-BSC")
    
    exercise_1()
    exercise_2()
    exercise_3()

    


    
    
    
    
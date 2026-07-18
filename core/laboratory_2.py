from operator import le

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcol
from scipy.special import erfc


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



class Digital_Signal_Information:
    def __init__(self,signal_power, n_bit_mod):
        self.__signal_power = signal_power
        self.__n_bit_mod = n_bit_mod
        self.__noise_power = 0

    @property
    def signal_power(self):
        return self.__signal_power
    
    @signal_power.setter
    def signal_power(self, value):
        self.__signal_power = value

    @property
    def n_bit_mod(self):
        return self.__n_bit_mod

    @n_bit_mod.setter
    def n_bit_mod(self, value):
        self.__n_bit_mod = value

    @property
    def noise_power(self):
        return self.__noise_power

    @noise_power.setter
    def noise_power(self, value):
        self.__noise_power = value
    

class Line:
    def __init__(self, loss_coefficient, length):
        self.__loss_coefficient = loss_coefficient
        self.__length = length

    @property
    def loss_coefficient(self):
        return self.__loss_coefficient

    @loss_coefficient.setter
    def loss_coefficient(self, value):
        self.__loss_coefficient = value

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value

    @property
    def loss(self):
        return self.loss_coefficient*(self.length/1000)
    
    def noise_generation(self, signal_power):
        return 1e-9*signal_power*self.length
    
    def snr_digital(self, signal_power):
        p_tx_dbm = lin2db(signal_power/0.001)
        p_noise_dbm = lin2db(self.noise_generation(signal_power)/0.001)
        return p_tx_dbm - p_noise_dbm - self.loss



class PCM:
    def __init__(self, digital_signal_info, adc, line):
        self.digital_signal_info = digital_signal_info
        self.adc = adc
        self.line = line
    
    def snr(self):
        snr_db = self.line.snr_digital(self.digital_signal_info.signal_power)
        return db2lin(snr_db)

    
    def ber_evaluation(self):
        snr_lin = self.snr()
        n_bit = self.digital_signal_info.n_bit_mod
        
        if n_bit == 1:
            ber = .5*erfc(np.sqrt(snr_lin))
        elif n_bit == 2:
            ber = .5*erfc(np.sqrt(snr_lin/2))
        elif n_bit == 3:
            ber = (2/3)*erfc(np.sqrt((3/14)*snr_lin))
        elif n_bit == 4:
            ber = (3/8)*erfc(np.sqrt(snr_lin/10))
        
        return ber

    def critical_pe(self):
        M = self.M
        return 1 / (4 * (M**2 - 1))
    
    def minimum_sampling_frequency(self):
        
        minimum_fs = 2 * self.analog_bandwidth
        n_steps = np.ceil(minimum_fs / ADC.fs_step)
    
        return n_steps * ADC.fs_step





def simulate(alpha, ber_th):
    signal_power = 0.001
    lengths_km = np.linspace(10, 120, 200)
    lengths_m = lengths_km * 1000
    n_bit_mods = np.array([1, 2, 3, 4])
    n_bit_adc = 6
    mod_names = {1: 'BPSK', 2: 'QPSK', 3: '8QAM', 4: '16QAM'}


    adc = ADC(n_bit_adc)

    results = {}

    for n_bit_mod in n_bit_mods:
        digital_signal_info = Digital_Signal_Information(signal_power, n_bit_mod)

    
        line = Line(alpha, lengths_m)
        pcm = PCM(digital_signal_info, adc, line)
        snr_db = pcm.line.snr_digital(signal_power)
        ber = pcm.ber_evaluation()
        
        results[mod_names[n_bit_mod]] = {
            'snr_db': snr_db,
            'ber': ber
        }


    return lengths_km, results

def plot(lengths_km, results, ber_th, name=""):

    # log10(ber) vs snr curves
    plt.figure()
    plt.ylim([-30, 0.1])
    
    with np.errstate(divide='ignore'):
        for mod_name in results:
            ber = results[mod_name]['ber']
            log_ber = np.log10(ber)
            snr = results[mod_name]['snr_db']
            
            plt.plot(snr, log_ber, label=mod_name)

            sort_indices = np.argsort(snr)
            snr_sorted = snr[sort_indices]
            ber_sorted = ber[sort_indices]

            clean_i = np.where(ber_sorted < ber_th)[0]
            if len(clean_i) > 0:
                clean_i_1 = clean_i[0]
                snr_min = snr_sorted[clean_i_1]
                
                plt.axvline(x=snr_min, color="purple", linestyle='--', alpha=0.8, 
                            label=f'{mod_name} Min SNR ({snr_min:.1f} dB)')

    plt.xlim(left=-1)
    plt.title("(log10(BER) vs SNR)")
    plt.axhline(np.log10(ber_th), color='red', linestyle='--', label=f'BER Threshold ({ber_th})')
    plt.legend()

    plt.xlabel('SNR(dB)')
    plt.ylabel('log10(BER)')
    plt.grid(True)
    plt.minorticks_on()
    
  
    plt.savefig(f"./curves/log10(BER) vs SNR{name}")
    plt.show()
    plt.clf()

    # Log10(ber) vs length curves
    plt.figure()
    plt.clf()
    plt.ylim([-30, 0.1])
    with np.errstate(divide='ignore'):
        for mod_name in results:
            ber = results[mod_name]['ber']
            log_ber = np.log10(ber)
            
            plt.plot(lengths_km, log_ber, label=mod_name)

            crossed_idxs = np.where(ber > ber_th)[0] 
            if len(crossed_idxs) > 0:
                first_failure_i = crossed_idxs[0]
                l_max = lengths_km[first_failure_i]
                
                plt.axvline(x=l_max, color='purple', linestyle='--', alpha=0.8, 
                            label=f'{mod_name} Lmax ({l_max:.1f} km)')
    
    plt.title("(log10(BER) vs Length)")
    plt.axhline(np.log10(ber_th), color='red', linestyle='--', label=f'BER Threshold ({ber_th})')
    plt.legend()

    plt.xlabel('Length(km)')
    plt.ylabel('log10(BER)')
    plt.grid(True)
    plt.minorticks_on()
    
    
    plt.savefig(f"./curves/log10(BER) vs Length{name}")
    plt.show()
    plt.clf()


if __name__ == "__main__":
    # BER = 10^-2
    lengths_km1, results1 = simulate(1, 1e-2)

    plot(lengths_km1,results1, 1e-2)

    # BER = 10^-3
    lengths_km2, results2 = simulate(1, 1e-3)

    plot(lengths_km2,results2,1e-3, "(ber_th=10^-3)")
    
    # new alpha
    ber_th = 1e-3
    alphas = [0.2,0.5,2]

    for alpha in alphas:
        lengths_km, result = simulate(alpha, ber_th)
        plot(lengths_km, result,ber_th, f"(alpha={str(alpha).replace('.', '_')}")

        

    
    
    
    
import getopt
import os
import sys
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import csv

DOT_DELIMITER = '.'
COMMA_DELIMITER = ','
INFO_TAG = "[*]"
IP_V4_LENGTH = 32
NUMBER_OF_OCTS = IP_V4_LENGTH // 8
BITS_IN_OCT = 255


def print_help():
    messagebox.showinfo('Pomoc', 'Aby policzyć podsieci vlsm, wpisz adres sieci w formacie xxx.xxx.xxx.xxx, prefiks /xx i '
                                 'liczbę hostów w każdej podsieci')

def print_info(message):
    print("{0} {1} {2}".format(INFO_TAG, message, INFO_TAG))



def convert_input_to_array(data, delimiter):
    data = data.split(delimiter)
    data = list(map(int, data))
    return data


def convert_slash_mask_to_address(mask):
    address_mask = []

    mask = int(mask[1:])

    for i in range(NUMBER_OF_OCTS):
        if mask >= 8:
            address_mask.append(255)
            mask -= 8
        elif mask > 0:
            address_mask.append(int("1" * mask + "0" * (8 - mask), 2))
            mask = 0
        else:
            address_mask.append(0)

    return address_mask


def find_optimal_mask(host_demand):
    host_capacity = 0
    power = 1

    while host_capacity < host_demand:
        power += 1
        host_capacity = (2 ** power) - 2

    return convert_slash_mask_to_address("/" + str(IP_V4_LENGTH - power))


def add_full_range(network, mask):
    network_copy = list(network)
    mask_copy = list(mask)

    for i in range(NUMBER_OF_OCTS):
        mask_copy[i] ^= 255
        network_copy[i] += mask_copy[i]
    return network_copy, mask_copy


def check_overflow(network):
    for i in range(NUMBER_OF_OCTS - 1, -1, -1):
        if network[i] > BITS_IN_OCT:
            if i == 0:
                raise Exception("Operation exceeded IPv4 range")
            network[i] -= (BITS_IN_OCT + 1)
            network[i - 1] += 1


def add_one_to_network(network):
    network[NUMBER_OF_OCTS - 1] += 1


def subtract_one_from_network(network):
    for i in range(NUMBER_OF_OCTS - 1, -1, -1):
        if network[i] != 0:
            network[i] -= 1
            break


def calculate_next_network(current_network, current_mask):
    network, mask = add_full_range(current_network, current_mask)
    add_one_to_network(network)
    check_overflow(network)

    return network


def is_network_valid(network_to_validate, whole_network, mask):
    for i in range(NUMBER_OF_OCTS):
        if network_to_validate[i] & mask[i] != whole_network[i]:
            return False

    return True


def calculate_networks(network, mask, hosts):
    whole_network = list(network)
    result = []

    current_network = list(network)
    for host_number in hosts:
        current_mask = find_optimal_mask(host_number)
        result.append((current_network, current_mask))

        current_network = calculate_next_network(current_network, current_mask)
        if not is_network_valid(current_network, whole_network, mask):
                raise Exception("Liczba hostów przekroczyła pojemność danej sieci")

    return result


def calculate_available_addresses(networks):
    networks_count = len(networks)
    available_addresses = []

    for i in range(networks_count):
        network_copy = list(networks[i][0])
        mask_copy = list(networks[i][1])

        broadcast_address = add_full_range(network_copy, mask_copy)[0]
        add_one_to_network(network_copy)
        check_overflow(network_copy)
        first_address = network_copy
        last_address = list(broadcast_address)
        subtract_one_from_network(last_address)

        available_addresses.append((first_address, last_address, broadcast_address))

    return available_addresses


def convert_ip_to_str(address):
    return DOT_DELIMITER.join(str(x) for x in address)


def print_result(networks, demanded_hosts, available_addresses):
    networks_count = len(networks)
    for i in range(networks_count):
        network = networks[i][0]
        mask = networks[i][1]
        broadcast = available_addresses[i][2]
        first_address = available_addresses[i][0]
        last_address = available_addresses[i][1]

        subn_addr[i].configure(state="normal")
        subn_addr[i].insert(0, convert_ip_to_str(network))
        subn_addr[i].configure(state=DISABLED)

        subn_mask[i].configure(state="normal")
        subn_mask[i].insert(0, convert_ip_to_str(mask))
        subn_mask[i].configure(state=DISABLED)

        subn_broadcast[i].configure(state="normal")
        subn_broadcast[i].insert(0, convert_ip_to_str(broadcast))
        subn_broadcast[i].configure(state=DISABLED)

        subn_first[i].configure(state="normal")
        subn_first[i].insert(0, convert_ip_to_str(first_address))
        subn_first[i].configure(state=DISABLED)
        subn_last[i].configure(state="normal")
        subn_last[i].insert(0, convert_ip_to_str(last_address))
        subn_last[i].configure(state=DISABLED)



def correct_network(address, mask):
    for i in range(NUMBER_OF_OCTS):
        address[i] = address[i] & mask[i]

    return address


def check_network(address, mask):

    network_is_valid = is_network_valid(address, address, mask)
    if not network_is_valid:
        messagebox.showerror('Error', 'Wpisano nieprawidłowy adres sieci lub maskę')
        address = correct_network(address, mask)

    return address


def convert_oct_to_bin(oct):
    oct = bin(oct)[2:]
    l = len(oct)
    if l < 8:
        oct = "0" * (8 - l) + oct
    return oct


def print_ip_decimal(ip):
    s = convert_ip_to_str(ip)
    print(s)


def print_ip_binary(ip):
    s = DOT_DELIMITER.join(convert_oct_to_bin(i) for i in ip)
    return s


def print_ip(ip, is_decimal_form, is_binary_form):
    if is_decimal_form:
        print_ip_decimal(ip)
    if is_binary_form:
        print_ip_binary(ip)


def get_network(index):
    if index == 0:
        return

def clean_inputs():
    for i in range(0, 10):
        subn_hosts[i].delete(0, END)

        subn_addr[i].configure(state="normal")
        subn_addr[i].delete(0, END)
        subn_addr[i].configure(state=DISABLED)

        subn_mask[i].configure(state="normal")
        subn_mask[i].delete(0, END)
        subn_mask[i].configure(state=DISABLED)

        subn_first[i].configure(state="normal")
        subn_first[i].delete(0, END)
        subn_first[i].configure(state=DISABLED)

        subn_last[i].configure(state="normal")
        subn_last[i].delete(0, END)
        subn_last[i].configure(state=DISABLED)

        subn_broadcast[i].configure(state="normal")
        subn_broadcast[i].delete(0, END)
        subn_broadcast[i].configure(state=DISABLED)

    btn.configure(state="normal")
    clear_btn.configure(bg="Gainsboro")
    export_btn.configure(state=DISABLED)

def export_networks():
    root = Tk().withdraw()

    file = filedialog.asksaveasfile(mode='w', defaultextension=".csv")

    if file:
        hosts = list()

        for x in subn_hosts:
            hosts.append(x.get())

        hosts = list(filter(None, hosts))

        host_count = 0
        for x in hosts:
            host_count += 1

        for i in range(0, host_count):
            file.write("subnetwork")
            file.write(str(i+1))
            file.write(",")
            file.write(hosts[i])
            file.write(",")
            file.write(subn_addr[i].get())
            file.write(",")
            file.write(subn_mask[i].get())
            file.write(",")
            file.write(subn_first[i].get())
            file.write(",")
            file.write(subn_last[i].get())
            file.write(",")
            file.write(subn_broadcast[i].get())
            file.write("\n")
        file.close()
        export_btn.configure(state=DISABLED)

def calculate():
    network = glob_net.get()
    mask = mask_net.get()
    hosts = list()

    for x in subn_hosts:
        hosts.append(x.get())

    hosts = list(filter(None, hosts))
    print(hosts)

    try:
        hosts = list(map(int, hosts))
    except:
        messagebox.showerror('Error', 'Wpisz poprawne liczby hostów')
        return
    print(hosts)
    try:
        network = convert_input_to_array(network, DOT_DELIMITER)
    except:
        messagebox.showerror('Error', 'Wpisz poprawny adres sieci')
        return
    print(network)
    # hosts = convert_input_to_array(hosts, COMMA_DELIMITER)
    if mask[0] == '/' or mask[0] == '\\':
        mask = convert_slash_mask_to_address(mask)
        print(mask)
    else:
        # mask_err
        a = 1

    try:
        calculated_networks = calculate_networks(network, mask, hosts)
    except:
        messagebox.showerror('Error', 'Liczba hostów jest zbyt duża dla tej sieci')
    available_addresses = calculate_available_addresses(calculated_networks)
    print_result(calculated_networks, hosts, available_addresses)
    btn.configure(state=DISABLED)
    export_btn.configure(state="normal")
    orig_color = clear_btn.cget("background")
    clear_btn.configure(bg="lightblue")

window = Tk()
window.title("Subnet Calculator")
lbl = Label(window, text="Adres sieci")
lbl.grid(column=0, row=0)

glob_net = Entry(window, width=16)
glob_net.grid(column=1, row=0)
glob_net.insert(0, "192.168.0.0")
glob_net.focus()
mask_net = Entry(window, width=3)
mask_net.grid(column=2, row=0)
mask_net.insert(0, "/24")

btn = Button(window, text="Przelicz", command=calculate, activebackground="lightblue", highlightbackground="lightblue",
             bg="Gainsboro")
btn.grid(column=0, row=3)

clear_btn = Button(window, text="Wyczyść", command=clean_inputs, activebackground="lightblue",
                   highlightbackground="lightblue", bg="Gainsboro")
clear_btn.grid(column=4, row=14)

export_btn = Button(window, text="Exportuj", command=export_networks, activebackground="lightblue",
                    highlightbackground="lightblue", bg="Gainsboro", state=DISABLED)
export_btn.grid(column=5, row=14)

help_btn = Button(window, text="Pomoc", command=print_help, activebackground="lightblue",
                  highlightbackground="lightblue", bg="Gainsboro")
help_btn.grid(column=6, row=14)

lbl = Label(window, text="l. hostów")
lbl.grid(column=1, row=3)

lbl = Label(window, text="Adres podsieci")
lbl.grid(column=2, row=3)

lbl = Label(window, text="Maska")
lbl.grid(column=3, row=3)

lbl = Label(window, text="1szy użyt. adr.")
lbl.grid(column=4, row=3)

lbl = Label(window, text="Ostatni użyt. adr.")
lbl.grid(column=5, row=3)

lbl = Label(window, text="Broadcast")
lbl.grid(column=6, row=3)

subn_name      = list()
subn_addr      = list()
subn_hosts     = list()
subn_mask      = list()
subn_first     = list()
subn_last      = list()
subn_broadcast = list()
for i in range(0, 10):
    subn_name.append(i)
    name = "podsieć " + str(i + 1)
    subn_name[i] = Label(window, text=name)
    subn_name[i].grid(column=0, row=4 + i)

    subn_hosts.append(i)
    subn_hosts[i] = Entry(window, width=4)
    subn_hosts[i].grid(column=1, row=4 + i)

    subn_addr.append(i)
    subn_addr[i] = Entry(window, width=14)
    subn_addr[i].grid(column=2, row=4 + i)
    subn_addr[i].configure(state=DISABLED, disabledbackground="lightblue", disabledforeground="black")

    subn_mask.append(i)
    subn_mask[i] = Entry(window, width=14)
    subn_mask[i].grid(column=3, row=4 + i)
    subn_mask[i].configure(state=DISABLED, disabledbackground="lightblue", disabledforeground="black")

    subn_first.append(i)
    subn_first[i] = Entry(window, width=14)
    subn_first[i].grid(column=4, row=4 + i)
    subn_first[i].configure(state=DISABLED, disabledbackground="lightblue", disabledforeground="black")

    subn_last.append(i)
    subn_last[i] = Entry(window, width=14)
    subn_last[i].grid(column=5, row=4 + i)
    subn_last[i].configure(state=DISABLED, disabledbackground="lightblue", disabledforeground="black")

    subn_broadcast.append(i)
    subn_broadcast[i] = Entry(window, width=14)
    subn_broadcast[i].grid(column=6, row=4 + i)
    subn_broadcast[i].configure(state=DISABLED, disabledbackground="lightblue", disabledforeground="black")

window.geometry('820x300')
window.mainloop()
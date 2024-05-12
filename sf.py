import dns.resolver
import threading

def check_dns_status(url):
    try:
        result = dns.resolver.query(url, 'A')
        if not result.response.rcode() == dns.rcode.NOERROR:
            return 'SERVFAIL'
        return 'OK'
    except dns.exception.DNSException as e:
        if 'SERVFAIL' in str(e):
            return 'SERVFAIL'
        else:
            return str(e)

def read_file(filename):
    with open(filename, 'r') as f:
        website_list = f.read().splitlines()
    return website_list

def scan_websites(website_list, start_index, end_index):
    for i in range(start_index, end_index):
        website = website_list[i]
        status = check_dns_status(website)
        if status == 'SERVFAIL':
            with open('servfail.txt', 'a') as f:
                f.write(website + '\n')
        print(website + ' : ' + status)

litz = input("List: ")
website_list = read_file(litz)

# ubah thread disini
num_threads = 100
chunk_size = len(website_list) // num_threads
threads = []

for i in range(num_threads):
    start_index = i * chunk_size
    if i == num_threads - 1:
        end_index = len(website_list)
    else:
        end_index = (i + 1) * chunk_size
    thread = threading.Thread(target=scan_websites, args=(website_list, start_index, end_index))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

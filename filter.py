import dns.resolver
import dns.query
import dns.message
import dns.name
import colorama
import concurrent.futures
from colorama import Fore, init

init(autoreset=True)

def get_root_ns():
    return ['a.root-servers.net', 'b.root-servers.net', 'c.root-servers.net']

def query_ns(servers, name, rtype):
    for server in servers:
        try:
            ns_address = dns.resolver.resolve(server, 'A')[0].to_text()
            query = dns.message.make_query(name, rtype)
            response = dns.query.udp(query, ns_address)
            if response.rcode() == dns.rcode.NOERROR:
                return [rr.to_text() for rr in response.authority[0]]
        except Exception as e:
            continue
    return []

def get_tld_ns(domain):
    root_servers = get_root_ns()
    tld = dns.name.from_text(domain).parent()
    return query_ns(root_servers, tld, dns.rdatatype.NS)

def get_domain_ns(domain):
    tld_ns = get_tld_ns(domain)
    if not tld_ns:
        return []
    return query_ns(tld_ns, dns.name.from_text(domain), dns.rdatatype.NS)

def normalize_ns(ns):
    return ns.lower().strip('.')

ns_groups = {
    "000domains": ["ns1.000domains.com", "ns2.000domains.com", "fwns1.000domains.com", "fwns2.000domains.com"],
    "digitalocean": ["ns1.digitalocean.com", "ns2.digitalocean.com", "ns3.digitalocean.com"],
    "dnsmadeeasy": ["dnsmadeeasy.com", "ns1.dnsmadeeasy.com", "ns2.dnsmadeeasy.com", "ns3.dnsmadeeasy.com", "ns4.dnsmadeeasy.com"],
    "dnsimple": ["ns1.dnsimple.com", "ns2.dnsimple.com", "ns3.dnsimple.com", "ns4.dnsimple.com"],
    "domain": ["ns1.domain.com", "ns2.domain.com"],
    "dotster": ["ns1.dotster.com", "ns2.dotster.com", "ns1.nameresolve.com", "ns2.nameresolve.com"],
    "easydns": ["dns1.easydns.com", "dns2.easydns.net", "dns3.easydns.org", "dns4.easydns.info"],
    "hurricaneelectric": ["ns5.he.net", "ns4.he.net", "ns3.he.net", "ns2.he.net", "ns1.he.net"],
    "linode": ["ns1.linode.com", "ns2.linode.com"],
    "mydomain": ["ns1.mydomain.com", "ns2.mydomain.com"],
    "tierranet": ["ns1.domaindiscover.com", "ns2.domaindiscover.com"],
    "a2hosting": ["ns1.a2hosting.com", "ns2.a2hosting.com","ns3.a2hosting.com","ns4.a2hosting.com"],
}

def process_domain(domain):
    try:
        print(f"Sedang memproses domain: {domain}")
        domain_ns = get_domain_ns(domain)

        if domain_ns:
            print("Nameserver untuk domain:", domain)
            for ns in domain_ns:
                print(ns)
        else:
            print("Tidak dapat menemukan nameserver, mungkin terjadi SERVFAIL atau masalah lain.")

        matched_group = None
        for ns in domain_ns:
            for group, group_ns in ns_groups.items():
                if normalize_ns(ns) in [normalize_ns(group_ns) for group_ns in group_ns]:
                    matched_group = group
                    break

        status = "berhasil" if domain_ns else "gagal"

        if status == "gagal":
            status_color = Fore.RED
        else:
            status_color = Fore.GREEN

        print(f"{domain} => {status_color}{status}")

        if matched_group is not None and status == "berhasil":
            with open(f"{matched_group}.txt", "a") as group_file:
                group_file.write(f"Domain: {domain}\nNameservers: {', '.join(domain_ns)}\nStatus: {status}\n\n")
        elif status == "berhasil":
            with open("random-ns.txt", "a") as file:
                file.write(f"Domain: {domain}\nNameservers: {', '.join(domain_ns)}\nStatus: {status}\n\n")
    except Exception as e:
        print(f"Error processing domain {domain}: {e}")

def main():
    colorama.init(autoreset=True)
    file_path = input("Masukkan path file yang berisi daftar domain: ")
    domains = []
    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_domain, domain) for domain in domains]

if __name__ == "__main__":
    main()

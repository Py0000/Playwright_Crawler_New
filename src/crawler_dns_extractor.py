import dns.resolver
import json
import os

import util
import util_def

NO_RECORDS_FLAG = "No records found"
DNS_EXCEPTION = "DNS Exception occurred"
ERROR_RESULTS = [[NO_RECORDS_FLAG], [DNS_EXCEPTION]]

def get_A_records(domain, resolver):
    record_type = 'A'
    a_records = {
        'IPv4 Address (Value)': []
    }

    try:
        response = resolver.resolve(domain, record_type)

        for rdata in response:
            value = str(rdata)
            a_records['IPv4 Address (Value)'].append(value)
        
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # If no records of the specified type are found, move on to the next record type
        a_records = [NO_RECORDS_FLAG]
    except Exception:
        a_records = [DNS_EXCEPTION]

    return a_records


def get_AAAA_records(domain, resolver):
    record_type = 'AAAA'
    aaaa_records = {
        'IPv6 Address (Value)': []
    }

    try:
        response = resolver.resolve(domain, record_type)

        for rdata in response:
            value = str(rdata)
            aaaa_records['IPv6 Address (Value)'].append(value)
        
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # If no records of the specified type are found, move on to the next record type
        aaaa_records = [NO_RECORDS_FLAG]
    except Exception:
        aaaa_records = [DNS_EXCEPTION]

    return aaaa_records


def get_CAA_records(domain, resolver):
    record_type = 'CAA'
    caa_records = {
        'Flag': [],
        'Tag': [],
        'Value': [],
    }

    try:
        response = resolver.resolve(domain, record_type)

        for rdata in response:
            caa_flag = rdata.caa_flag
            caa_tag = rdata.caa_tag.decode()
            caa_value = rdata.caa_value.decode()

            caa_records['Flag'].append(caa_flag)
            caa_records['Tag'].append(caa_tag)
            caa_records['Value'].append(caa_value)
  
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # If no records of the specified type are found, move on to the next record type
        caa_records = [NO_RECORDS_FLAG]
    except Exception:
        caa_records = [DNS_EXCEPTION]

    return caa_records


def get_CNAME_records(domain, resolver):
    record_type = 'CNAME'
    cname_records = {
        'Host Name Alias': [],
    }

    try:
        response = resolver.resolve(domain, record_type)

        for rdata in response:
            value = str(rdata)

            cname_records['Host Name Alias'].append(value)

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # If no records of the specified type are found, move on to the next record type
        cname_records = [NO_RECORDS_FLAG]
    except Exception:
        cname_records = [DNS_EXCEPTION]

    return cname_records


def get_MX_records(domain, resolver):
    record_type = 'MX'
    mx_records = {
        'Preference': [],
        'Exchange': [],
    }

    try:
        response = resolver.resolve(domain, record_type)

        for rdata in response:
            priority = rdata.preference
            target = str(rdata.exchange)

            mx_records['Preference'].append(priority)
            mx_records['Exchange'].append(target)

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # If no records of the specified type are found, move on to the next record type
        mx_records = [NO_RECORDS_FLAG]
    except Exception:
        mx_records = [DNS_EXCEPTION]

    return mx_records


def get_NS_records(domain, resolver):
    record_type = 'NS'
    ns_records = {
        'Name Server': [],
    }

    try:
        response = resolver.resolve(domain, record_type)

        for rdata in response:
            value = str(rdata)

            ns_records['Name Server'].append(value)

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # If no records of the specified type are found, move on to the next record type
        ns_records = [NO_RECORDS_FLAG]
    except Exception:
        ns_records = [DNS_EXCEPTION]

    return ns_records


def get_SOA_records(domain, resolver):
    record_type = 'SOA'
    soa_records = {
        'MNAME': [],
        'RNAME': [],
        'SERIAL': [],
        'REFRESH': [],
        'RETRY': [],
        'EXPIRE': [],
        'MINIMUM': [],
    }

    try:
        response = resolver.resolve(domain, record_type)

        for rdata in response:
            mname = str(rdata.mname)
            rname = str(rdata.rname)
            serial = rdata.serial
            refresh = rdata.refresh
            retry = rdata.retry
            expire = rdata.expire
            minimum = rdata.minimum

            soa_records['MNAME'].append(mname)
            soa_records['RNAME'].append(rname)
            soa_records['SERIAL'].append(serial)
            soa_records['REFRESH'].append(refresh)
            soa_records['RETRY'].append(retry)
            soa_records['EXPIRE'].append(expire)
            soa_records['MINIMUM'].append(minimum)


    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # If no records of the specified type are found, move on to the next record type
        soa_records = [NO_RECORDS_FLAG]
    except Exception:
        soa_records = [DNS_EXCEPTION]

    return soa_records


def get_TXT_records(domain, resolver):
    record_type = 'TXT'
    txt_records = {
        'Text Data': [],
    }

    try:
        response = resolver.resolve(domain, record_type)

        for rdata in response:
            text_data = ' '.join([item.decode() for item in rdata.strings])

            txt_records['Text Data'].append(text_data)

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # If no records of the specified type are found, move on to the next record type
        txt_records = [NO_RECORDS_FLAG]
    except Exception:
        txt_records = [DNS_EXCEPTION]

    return txt_records


def extract_dns_records(website_url, folder_path):
    try:
        domain = util.extract_hostname(website_url)

        # Create a DNS resolver object
        resolver = dns.resolver.Resolver()

        dns_records = {
            'Website': website_url,
            'Domain': domain,
            'A': get_A_records(domain, resolver),
            'AAAA': get_AAAA_records(domain, resolver),
            'CAA': get_CAA_records(domain, resolver),
            'CNAME': get_CNAME_records(domain, resolver),
            'MX': get_MX_records(domain, resolver),
            'NS': get_NS_records(domain, resolver),
            'SOA': get_SOA_records(domain, resolver),
            'TXT': get_TXT_records(domain, resolver)
        }

        dns_records_json_output_path = os.path.join(folder_path, util_def.FILE_DNS)
        util.save_data_to_json_format(dns_records_json_output_path, dns_records)

        print("DNS info saved... ")
        status = "Success"

    except Exception as e:
        print("DNS Records Extraction Error: ", e)
        status = "Failed"
    
    finally:
        return status
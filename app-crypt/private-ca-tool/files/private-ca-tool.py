#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os,subprocess,logging,argparse

CA_KEY = '/etc/ssl/private/ca.key'
CA_CERT = '/usr/local/share/ca-certificates/ca.crt'

def create(days=3650, overwrite=False):
    if not overwrite and os.path.exists(CA_CERT):
        logging.info(f"CA certificate {CA_CERT} already exists. Use --overwrite to recreate.")
        return
    #else
    os.makedirs(os.path.dirname(CA_CERT), exist_ok=True)
    subprocess.run([
        'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
        '-keyout', CA_KEY, '-out', CA_CERT, '-days', str(days),
        '-nodes', '-subj', '/C=JP/ST=Tokyo/O=WBRXCORP/CN=walbrix.com'
    ], check=True)
    subprocess.run(['update-ca-certificates'], check=True)
    logging.info(f"CA certificate {CA_CERT} created.")

def generate_server_cert(cn, alt_names, server_key, server_cert, days=3650, overwrite=False):
    if not overwrite and os.path.exists(server_cert):
        logging.info(f"Server certificate {server_cert} already exists. Use --overwrite to recreate.")
        return
    #else
    subprocess.run([
        'openssl', 'genrsa', '-out', server_key, '2048'
    ], check=True)

    if alt_names is None:
        alt_names = 'DNS:' + cn

    req = subprocess.run([
        'openssl', 'req', '-new', '-key', server_key,
        '-subj', f'/CN={cn}',
        '-addext', f'subjectAltName={alt_names}'
    ], check=True, capture_output=True)
    csr = req.stdout

    subprocess.run([
        'openssl', 'x509', '-req', '-CA', CA_CERT, '-CAkey', CA_KEY,
        '-CAcreateserial', '-out', server_cert, '-days', str(days),
        '-copy_extensions', 'copy'
    ], check=True, input=csr)
    logging.info(f"Server certificate {server_cert} created.")

def trust(nssdb_dir):
    if not os.path.exists(CA_CERT):
        raise FileNotFoundError(f"CA certificate {CA_CERT} does not exist. Please create it first.")
    if os.path.exists(nssdb_dir): return
    #else
    os.makedirs(nssdb_dir, exist_ok=True)
    subprocess.run([
        'certutil', '-d', f'sql:{nssdb_dir}', '-A', '-t', 'C,,', '-n', 'PrivateCA', '-i', CA_CERT
    ], check=True)
    logging.info(f'CA certificate added to NSS database at {nssdb_dir}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Private CA management tool")
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    # subcommands are create, generate-server-cert, trust-ca
    subparsers = parser.add_subparsers(dest='command', required=True)
    # create command
    create_parser = subparsers.add_parser('create', help='Create a new CA certificate')
    create_parser.add_argument('--days', type=int, default=3650, help='Validity period of the CA certificate in days')
    create_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing CA certificate')
    # generate-server-cert command
    gen_parser = subparsers.add_parser('generate-server-cert', help='Generate a server certificate')
    gen_parser.add_argument('cn', help='Common Name for the server certificate')
    gen_parser.add_argument('--alt-names', help='Subject Alternative Names for the server certificate, comma-separated')
    gen_parser.add_argument('--server-key', default='/etc/ssl/private/server.key', help='Path to the server private key')
    gen_parser.add_argument('--server-cert', default='/etc/ssl/certs/server.crt', help='Path to the server certificate')
    gen_parser.add_argument('--days', type=int, default=3650, help='Validity period of the server certificate in days')
    gen_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing server certificate')
    # trust-ca command
    trust_parser = subparsers.add_parser('trust', help='Trust the CA certificate in NSS database')
    trust_parser.add_argument('--nssdb-dir', default=os.path.expanduser('~/.pki/nssdb'), help='Path to the NSS database directory')
    
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    if args.command == 'create':
        create(days=args.days, overwrite=args.overwrite)
    elif args.command == 'generate-server-cert':
        generate_server_cert(
            cn=args.cn,
            alt_names=args.alt_names,
            server_key=args.server_key,
            server_cert=args.server_cert,
            days=args.days,
            overwrite=args.overwrite
        )
    elif args.command == 'trust':
        trust(
            nssdb_dir=args.nssdb_dir,
        )
    
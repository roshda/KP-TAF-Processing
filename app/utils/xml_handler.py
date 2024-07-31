import xml.etree.ElementTree as ET
from datetime import datetime
import os, re
import zipfile

def update_xml_recipient_status(xml_file_path, status, reason=None):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    current_datetime = datetime.now()
    received_date = current_datetime.strftime('%Y-%m-%d')
    received_time = current_datetime.strftime('%H:%M:%S')
    ship_date = current_datetime.strftime('%Y-%m-%d') if status == 'Shipped' else ''

    for recipient in root.findall('.//recipient'):
        for elem in list(recipient):
            if elem.tag in ['status', 'date', 'time', 'mail_tracking_number', 'reason', 'ShipDate', 'ShippingCost', 'Comments']:
                recipient.remove(elem)
        ET.SubElement(recipient, 'VendorID').text = 'N'
        ET.SubElement(recipient, 'OrderID').text = root.find('.//orderId').text
        ET.SubElement(recipient, 'ShipDate').text = ship_date
        ET.SubElement(recipient, 'ShippingMethod').text = 'USPS'
        ET.SubElement(recipient, 'ShippingCost').text = 'TBD'
        ET.SubElement(recipient, 'Comments').text = reason if reason else 'Good Record'
        ET.SubElement(recipient, 'PackagesCount').text = ''
        ET.SubElement(recipient, 'Tracking').text = ''
        ET.SubElement(recipient, 'status').text = status
        ET.SubElement(recipient, 'date').text = received_date
        ET.SubElement(recipient, 'time').text = received_time
        ET.SubElement(recipient, 'mail_tracking_number').text = ''
        ET.SubElement(recipient, 'reason').text = reason if reason else 'Good Record'

    return tree

def create_hdr_file(entries, vendor_id):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    hdr_filename = f"status_{timestamp}_{vendor_id}.hdr"
    with open(hdr_filename, 'w') as hdr:
        for entry in entries:
            hdr.write(f"ACCESS\t{entry['order_id']}\t{entry['status']}\t{entry['date']}\n")
    return hdr_filename

def rename_and_zip_return_files(order_path, order_id, timestamp, xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    zip_filename = f"RETURN_ALTERNATE_FORMAT_{order_id}_1_{timestamp}_order_PSP.zip"
    zip_filepath = os.path.join(order_path, zip_filename)
    done_filename = zip_filename.replace('.zip', '.done')
    done_filepath = os.path.join(order_path, done_filename)

    brf_files = [f for f in os.listdir(order_path) if f.endswith('.brf')]
    mp3_files = [f for f in os.listdir(order_path) if f.endswith('.mp3')]
    pdf_files = sorted(
        (f for f in os.listdir(order_path) if f.endswith('.pdf')),
        key=lambda x: os.path.getmtime(os.path.join(order_path, x)),
        reverse=True
    )

    if not brf_files and not mp3_files and pdf_files:
        latest_pdf = pdf_files[0]

    with zipfile.ZipFile(zip_filepath, 'w') as main_zip:
        for file in brf_files:
            doc_id = file.split('_')[0]
            new_name = f"RETURN_ALTERNATE_FORMAT_{doc_id}_BRAILLE{os.path.splitext(file)[1]}"
            file_path = os.path.join(order_path, file)
            new_path = os.path.join(order_path, new_name)
            os.rename(file_path, new_path)
            main_zip.write(new_path, arcname=new_name)

        if mp3_files:
            doc_groups = {}
            for file in mp3_files:
                doc_id_match = re.match(r"^(.+?)_(\d+)\.mp3$", file)
                if doc_id_match:
                    doc_id = doc_id_match.group(1)
                    if doc_id not in doc_groups:
                        doc_groups[doc_id] = []
                    doc_groups[doc_id].append(file)

            for doc_id, files in doc_groups.items():
                subzip_name = f"RETURN_ALTERNATE_FORMAT_{doc_id}_AUDIO.zip"
                subzip_path = os.path.join(order_path, subzip_name)
                with zipfile.ZipFile(subzip_path, 'w') as subzip:
                    for file in files:
                        file_path = os.path.join(order_path, file)
                        subzip.write(file_path, arcname=file)
                main_zip.write(subzip_path, arcname=subzip_name)
                os.remove(subzip_path)

        if not brf_files and not mp3_files and pdf_files:
            file = latest_pdf
            doc_id = file.split('_')[0]
            new_name = f"RETURN_ALTERNATE_FORMAT_{doc_id}_ACCESSIBLE_DOCUMENT{os.path.splitext(file)[1]}"
            file_path = os.path.join(order_path, file)
            new_path = os.path.join(order_path, new_name)
            os.rename(file_path, new_path)
            main_zip.write(new_path, arcname=new_name)

    open(done_filepath, 'a').close()
    return zip_filepath, done_filepath

import qrcode

def generate_qr_code(address):
    filename = f"qrcode_{address[-6:]}.png"
    img = qrcode.make(address)
    img.save(filename)
    return filename

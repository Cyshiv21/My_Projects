import qrcode
data = input("Enter URL: ").strip()
filename = input("Enter filename: ").strip()
qr = qrcode.QRCode(box_size=10, border=4)
qr.add_data(data)
img = qr.make_image(fill_color = "black", back_color = "white")
type(img)  # qrcode.image.pil.PilImage
img.save(f'{filename}.png')
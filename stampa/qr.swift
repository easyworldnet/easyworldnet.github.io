// Prints the QR modules for a URL as rows of 0/1 (no quiet zone).
// Uses macOS CoreImage, so nothing needs installing. Called by genera.py.
import CoreImage
import Foundation

let url = CommandLine.arguments[1]
let filter = CIFilter(name: "CIQRCodeGenerator")!
filter.setValue(url.data(using: .utf8), forKey: "inputMessage")
filter.setValue("Q", forKey: "inputCorrectionLevel")  // ~25% damage tolerance for printed posters
let image = filter.outputImage!
let ctx = CIContext()
let cg = ctx.createCGImage(image, from: image.extent)!
let w = cg.width, h = cg.height
var px = [UInt8](repeating: 0, count: w * h)
let gray = CGContext(data: &px, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w,
                     space: CGColorSpaceCreateDeviceGray(), bitmapInfo: 0)!
gray.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
let dark = (0..<h).map { y in (0..<w).map { x in px[y * w + x] < 128 } }
// CoreImage adds its own border; crop to the dark modules.
let rows = dark.indices.filter { dark[$0].contains(true) }
let cols = (0..<w).filter { x in dark.contains { $0[x] } }
for y in rows.first!...rows.last! {
  print((cols.first!...cols.last!).map { dark[y][$0] ? "1" : "0" }.joined())
}

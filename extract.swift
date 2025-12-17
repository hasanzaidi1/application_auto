import Foundation
import PDFKit

guard CommandLine.arguments.count > 1 else {
    fputs("Usage: extract.swift <pdf>\n", stderr)
    exit(1)
}

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path)

guard let doc = PDFDocument(url: url) else {
    fputs("Unable to open PDF\n", stderr)
    exit(1)
}

var output = ""
for index in 0..<doc.pageCount {
    if let page = doc.page(at: index) {
        output += (page.string ?? "")
        output += "\n\n"
    }
}
print(output)

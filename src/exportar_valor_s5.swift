// Exportação local, sem dependências externas. macOS: swift src/exportar_valor_s5.swift
import AppKit
import CoreGraphics
import PDFKit

let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
let folder = root.appendingPathComponent("dados/saidas/s5_valor_priorizacao")
let input = folder.appendingPathComponent("John_Valor_Priorizacao_S5.md")
let output = folder.appendingPathComponent("John_Valor_Priorizacao_S5.pdf")
let text = try String(contentsOf: input, encoding: .utf8)
let w: CGFloat = 595.28, h: CGFloat = 841.89, margin: CGFloat = 43
var box = CGRect(x: 0, y: 0, width: w, height: h)
guard let pdf = CGContext(output as CFURL, mediaBox: &box, nil) else { fatalError("Não abriu PDF") }
let ink = NSColor(calibratedRed: 0.11, green: 0.18, blue: 0.24, alpha: 1)
let teal = NSColor(calibratedRed: 0.02, green: 0.44, blue: 0.48, alpha: 1)
let pale = NSColor(calibratedRed: 0.93, green: 0.96, blue: 0.97, alpha: 1)
var y: CGFloat = margin
var page = 0

func attributed(_ value: String, size: CGFloat = 10, bold: Bool = false, color: NSColor? = nil) -> NSAttributedString {
    let para = NSMutableParagraphStyle()
    para.lineSpacing = 3
    para.lineBreakMode = .byWordWrapping
    return NSAttributedString(string: value.replacingOccurrences(of: "`", with: ""), attributes: [
        .font: bold ? NSFont.boldSystemFont(ofSize: size) : NSFont.systemFont(ofSize: size),
        .foregroundColor: color ?? ink,
        .paragraphStyle: para
    ])
}

func measured(_ attr: NSAttributedString, _ width: CGFloat) -> CGFloat {
    ceil(attr.boundingRect(with: NSSize(width: width, height: 2000), options: [.usesLineFragmentOrigin, .usesFontLeading]).height) + 5
}

func draw(_ attr: NSAttributedString, x: CGFloat, top: CGFloat, width: CGFloat, height: CGFloat) {
    attr.draw(with: NSRect(x: x, y: h-top-height, width: width, height: height), options: [.usesLineFragmentOrigin, .usesFontLeading])
}

func beginPage() {
    if page > 0 { pdf.endPDFPage() }
    pdf.beginPDFPage(nil)
    page += 1
    NSGraphicsContext.current = NSGraphicsContext(cgContext: pdf, flipped: false)
    y = margin
    if page > 1 {
        draw(attributed("VITALIZA  |  VALOR E PRIORIZAÇÃO", size: 8, bold: true, color: teal), x: margin, top: 20, width: w-2*margin, height: 12)
    }
    pdf.setStrokeColor(teal.cgColor)
    pdf.setLineWidth(0.5)
    pdf.move(to: CGPoint(x: margin, y: 35))
    pdf.addLine(to: CGPoint(x: w-margin, y: 35))
    pdf.strokePath()
    draw(attributed("John  |  Semana 5  |  Corte: 30/09/2026", size: 7.5), x: margin, top: h-30, width: 400, height: 12)
    draw(attributed(String(page), size: 8), x: w-margin-20, top: h-30, width: 20, height: 12)
}

func ensure(_ needed: CGFloat) {
    if y + needed > h-53 { beginPage() }
}

func paragraph(_ value: String, level: Int = 0) {
    let size: CGFloat = level == 1 ? 24 : (level == 2 ? 14 : 9.5)
    let attr = attributed(value, size: size, bold: level>0, color: level>0 ? teal : ink)
    let height = measured(attr, w-2*margin)
    ensure(height + (level>0 ? 55 : 10))
    if level>0 { y += 8 }
    draw(attr, x: margin, top: y, width: w-2*margin, height: height+2)
    y += height + (level>0 ? 10 : 8)
}

func table(_ lines: [String]) {
    let rows = lines.filter { !$0.contains("---") }.map { line in
        line.split(separator: "|", omittingEmptySubsequences: false).dropFirst().dropLast().map { $0.trimmingCharacters(in: .whitespaces) }
    }
    guard let first = rows.first else { return }
    let n = first.count
    let usable = w-2*margin
    var shares = Array(repeating: CGFloat(1)/CGFloat(n), count: n)
    if n==5 { shares = [0.14,0.22,0.14,0.22,0.28] }
    if n==3 { shares = [0.25,0.53,0.22] }
    if n==4 { shares = [0.25,0.25,0.25,0.25] }
    if n==6 { shares = [0.15,0.37,0.12,0.13,0.13,0.10] }
    if first.first=="Dimensão" { shares = [0.15,0.43,0.12,0.16,0.14] }
    if first.first=="Fonte" { shares = [0.20,0.64,0.16] }
    if n==2 { shares = [0.63,0.37] }
    func rowHeight(_ row: [String]) -> CGFloat {
        zip(row, shares).map { measured(attributed($0.0, size: 7.9), usable*$0.1-12) }.max()!+14
    }
    func render(_ row: [String], header: Bool) {
        let height = rowHeight(row)
        var x = margin
        for (idx,cell) in row.enumerated() {
            let cw=usable*shares[idx]
            (header ? teal : pale).setFill()
            NSRect(x:x,y:h-y-height,width:cw,height:height).fill()
            draw(attributed(cell,size:7.9,bold:header,color:header ? NSColor.white : ink),x:x+6,top:y+6,width:cw-12,height:height-10)
            NSColor.white.setStroke()
            let path=NSBezierPath(rect:NSRect(x:x,y:h-y-height,width:cw,height:height)); path.lineWidth=1;path.stroke()
            x += cw
        }
        y += height
    }
    ensure(rowHeight(first)+rowHeight(rows.count>1 ? rows[1] : first))
    render(first,header:true)
    for row in rows.dropFirst() {
        if y+rowHeight(row)>h-53 { beginPage(); render(first,header:true) }
        render(row,header:false)
    }
    y += 12
}

beginPage()
let lines = text.components(separatedBy: .newlines)
var i=0
while i<lines.count {
    let line=lines[i].trimmingCharacters(in:.whitespaces)
    if line.hasPrefix("|") {
        var block:[String]=[]
        while i<lines.count && lines[i].hasPrefix("|") { block.append(lines[i]);i+=1 }
        table(block)
        continue
    }
    if !line.isEmpty {
        if line.hasPrefix("# ") { paragraph(String(line.dropFirst(2)),level:1) }
        else if line.hasPrefix("## ") { paragraph(String(line.dropFirst(3)),level:2) }
        else { paragraph(line) }
    }
    i+=1
}
pdf.endPDFPage()
pdf.closePDF()
guard let doc=PDFDocument(url:output), doc.pageCount==page else { fatalError("Falha na validação do PDF") }
let scratch=URL(fileURLWithPath:"/tmp/vitaliza-s5-pdf-review",isDirectory:true)
try FileManager.default.createDirectory(at:scratch,withIntermediateDirectories:true)
for index in 0..<doc.pageCount {
    let p=doc.page(at:index)!
    let image=p.thumbnail(of:NSSize(width:900,height:1274),for:.mediaBox)
    guard let tiff=image.tiffRepresentation,let rep=NSBitmapImageRep(data:tiff),let png=rep.representation(using:.png,properties:[:]) else { fatalError("Falha ao renderizar") }
    try png.write(to:scratch.appendingPathComponent("pagina-\(index+1).png"))
}
print("PDF: \(output.path)\nPáginas: \(page)\nRevisão visual: \(scratch.path)")

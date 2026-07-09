package com.devops.incident.util;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * Minimal dependency-free PDF generator. Produces a single-stream, multi-line
 * text PDF suitable for exporting report content without external libraries.
 */
public final class PdfUtil {

    private PdfUtil() {
    }

    public static byte[] textToPdf(String title, String body) {
        List<String> lines = new ArrayList<>();
        if (title != null) {
            lines.add(title);
            lines.add("");
        }
        for (String raw : (body == null ? "" : body).split("\r?\n")) {
            // wrap long lines to ~90 chars
            String line = raw;
            while (line.length() > 90) {
                lines.add(line.substring(0, 90));
                line = line.substring(90);
            }
            lines.add(line);
        }

        StringBuilder text = new StringBuilder();
        text.append("BT\n/F1 11 Tf\n12 TL\n72 760 Td\n");
        for (String line : lines) {
            text.append("(").append(escape(line)).append(") Tj\nT*\n");
        }
        text.append("ET");

        byte[] streamBytes = text.toString().getBytes(StandardCharsets.ISO_8859_1);

        List<String> objects = new ArrayList<>();
        objects.add("<< /Type /Catalog /Pages 2 0 R >>");
        objects.add("<< /Type /Pages /Kids [3 0 R] /Count 1 >>");
        objects.add("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                + "/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>");
        objects.add("<< /Length " + streamBytes.length + " >>\nstream\n" + text + "\nendstream");
        objects.add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>");

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        StringBuilder pdf = new StringBuilder();
        pdf.append("%PDF-1.4\n");
        List<Integer> offsets = new ArrayList<>();
        for (int i = 0; i < objects.size(); i++) {
            offsets.add(pdf.toString().getBytes(StandardCharsets.ISO_8859_1).length);
            pdf.append(i + 1).append(" 0 obj\n").append(objects.get(i)).append("\nendobj\n");
        }
        int xrefOffset = pdf.toString().getBytes(StandardCharsets.ISO_8859_1).length;
        pdf.append("xref\n0 ").append(objects.size() + 1).append("\n");
        pdf.append("0000000000 65535 f \n");
        for (Integer offset : offsets) {
            pdf.append(String.format("%010d 00000 n %n", offset).replace("\r", ""));
        }
        pdf.append("trailer\n<< /Size ").append(objects.size() + 1).append(" /Root 1 0 R >>\n");
        pdf.append("startxref\n").append(xrefOffset).append("\n%%EOF");

        byte[] bytes = pdf.toString().getBytes(StandardCharsets.ISO_8859_1);
        out.writeBytes(bytes);
        return out.toByteArray();
    }

    private static String escape(String s) {
        if (s == null) {
            return "";
        }
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)");
    }
}

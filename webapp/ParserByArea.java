import org.apache.pdfbox.pdmodel.*;
import org.apache.pdfbox.text.*;

import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.io.IOException;
import java.awt.geom.Rectangle2D;

// called by Python script
// converts to text cropped areas of past paper as defined by Python script
// saves text in named text files in relevant paper's directory
// passes in arguments: path_to_pdf, path_to_save_dir, page_height, page_num, q_num, x0, y0, x1, y1
public class ParserByArea {

	public static void main(String[] args) {

		String paper_dir = args[1];
		String q_name = args[4];
		String text = "";
		PDDocument doc = null;

		try {

			File file = new File(args[0]);
			doc = PDDocument.load(file);

			double page_height = Double.parseDouble(args[2]);
			int page_num = Integer.parseInt(args[3]);

			// lower-left of crop region as from Python program
			double x0 = Double.parseDouble(args[5]);
			double y0 = Double.parseDouble(args[6]);

			// upper-right of crop region as from Python program
			double x1 = Double.parseDouble(args[7]);
			double y1 = Double.parseDouble(args[8]);

			// rectangle is defined from upper-left corner with width and height
			// add some minimal left/right padding to prevent any text being cropped out
			Rectangle2D.Double area = new Rectangle2D.Double(x0-5,(page_height-y1),(x1-x0)+5,(y1-y0));

			PDFTextStripperByArea area_strip = new PDFTextStripperByArea();
			area_strip.setSortByPosition(true);
			area_strip.addRegion("area", area);

			PDPage page = doc.getPage(page_num);
			area_strip.extractRegions(page);

			// remove empty lines/whitespace
			text = area_strip.getTextForRegion("area").replaceAll("(?m)^[ \t]*\r?\n", "");

		} catch (Exception e) {
			System.out.println(e.getMessage());
		} finally {
   			if( doc != null) {
   				try {
    				doc.close();
   				} catch (Exception e) {
   					System.err.println(e.getMessage());
   				}
   			}
   		}

   		// write text to file
   		BufferedWriter writer = null;
		try {
		    writer = new BufferedWriter(new FileWriter(paper_dir+q_name+".txt"));
		    writer.write(text);
		} catch (IOException e) {
			System.err.println(e.getMessage());
		} finally {
		    try {
		        if (writer != null)
		        	writer.close();
		    } catch (IOException e) {
		    	System.err.println(e.getMessage());
		    }
		}

	}

}
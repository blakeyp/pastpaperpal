import org.apache.pdfbox.pdmodel.*;
import org.apache.pdfbox.text.*;

import java.io.*;
import java.util.*;

import java.awt.geom.Rectangle2D;


// pass in as arguments: path_to_pdf, page_height, page_num, q_num, x0, y0, x1, y1

public class ParserByArea {

	public static void main(String[] args) {

		//PDDocument doc = new PDDocument();
		String text="";

		int q_num = -1;

		PDDocument doc = null;

		try {

			File file = new File(args[0]);   // input PDF file

			doc = PDDocument.load(file);

			double page_height = Double.parseDouble(args[1]);

			int page_num = Integer.parseInt(args[2]);

			q_num = Integer.parseInt(args[3]);

			// lower-left of crop region as from Python program
			double x0 = Double.parseDouble(args[4]);
			double y0 = Double.parseDouble(args[5]);

			// upper-right of crop region as from Python program
			double x1 = Double.parseDouble(args[6]);
			double y1 = Double.parseDouble(args[7]);

			// rectangle is defined from upper-left corner with width and height
			// add some minimal left/right padding to prevent any text being cropped out
			Rectangle2D.Double area = new Rectangle2D.Double(x0-5,(page_height-y1),(x1-x0)+5,(y1-y0));

			PDFTextStripperByArea area_strip = new PDFTextStripperByArea();

			area_strip.setSortByPosition(true);

			area_strip.addRegion("area", area);

			PDPage page = doc.getPage(page_num);

			area_strip.extractRegions(page);

			System.out.println("QUESTION " + q_num + "\n" + area_strip.getTextForRegion("area") + "\n");

			text = area_strip.getTextForRegion("area").replaceAll("(?m)^[ \t]*\r?\n", "");   // remove empty lines/whitespace

		} catch (Exception e) {
			System.out.println(e.getMessage());
		} finally {
   			if( doc != null) {
   				try {
    					doc.close();
   				} catch (Exception e) {
   					System.out.println(e.getMessage());
   				}
   			}
   		}



   		// write text to file

   		BufferedWriter writer = null;
		try
		{
		    writer = new BufferedWriter(new FileWriter("../questions/q"+q_num+".txt"));
		    writer.write(text);

		}
		catch ( IOException e)
		{
		}
		finally
		{
		    try
		    {
		        if ( writer != null)
		        writer.close( );
		    }
		    catch ( IOException e)
		    {
		    }
		}

	}

}
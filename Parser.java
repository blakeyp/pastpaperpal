import org.apache.pdfbox.pdmodel.*;
import org.apache.pdfbox.text.*;
import org.apache.pdfbox.pdmodel.interactive.documentnavigation.outline.PDOutlineItem;

import org.apache.pdfbox.cos.COSDictionary;

import java.io.*;

import java.util.*;

import java.util.regex.*;

public class Parser {

	public static void main(String[] args) {

		PDDocument doc = new PDDocument();
		String text="";

		try {

			File file = new File(args[0]+".pdf");   // input PDF file

			//File output = new File(args[1]+".txt");   // output text file

			doc = PDDocument.load(file);

			PDFTextStripper stripper = new PDFTextStripper();

			stripper.setSortByPosition(true);

			//stripper.setSpacingTolerance(0.9f);   // doesn't seem to make a difference?
			//stripper.setEndPage(1);

			text = stripper.getText(doc).replaceAll("(?m)^[ \t]*\r?\n", "");   // remove empty lines/whitespace

/*			BufferedWriter wr = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(output)));
			stripper.writeText(doc, wr);

			wr.close();*/

		} catch (Exception e) {
			System.out.println(e.getMessage());
		} finally {
   			if( doc != null) {
   				try {
    					doc.close();
    					System.out.println("Don't worry - done closing now!");
   				} catch (Exception e) {
   					System.out.println(e.getMessage());
   				}
   			}
   		}


   		// write text to file

   		BufferedWriter writer = null;
		try
		{
		    writer = new BufferedWriter(new FileWriter(args[0]+".txt"));
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

		// end

		/* doing this in python now
   		String[] lines = text.split("\n");
   		String line;

   		for (int i=0; i<lines.length;i++) {   // iterate over text line by line
   			line = lines[i].toLowerCase().trim();   // force case insensitivity, remove leading/trailing whitespace
   			//System.out.println(line);
   			if (line.matches(".*time.*:\\s*.*"))   // check if line might contain time details
   				parseTime(line);
   		*/


   		}


	}
	
	/* doing this in python now
	public static void parseTime(String next) {   // parses a line that is *suspected* to contain time details
		Pattern pattern = Pattern.compile(".*time.*:\\s*(?:([0-9]{1,2}(?:\\.[0-9]{0,2})?)\\s*(?:hours|hour|hrs|hr|hs|h))?\\s*([0-9]{1,3})?.*");   // regex to match time details
		Matcher matcher = pattern.matcher(next);
		matcher.matches();   // attempt to match

		String hrs = matcher.group(1);   // extract groups, capturing string representaions of hours and minutes
		String mins = matcher.group(2);

		if ((hrs == null) && (mins == null))   // nothing captured
			System.out.println("Sorry I thought I might be able to but I could not find a reasonable time duration from this line: " + next);
		else {
			hrs = (hrs == null) ? "0" : hrs;   // if no hours captured, set to 0
			mins = (mins == null) ? "0" : mins;   // if no mins captured, set to 0

			int h; int m;   // int representations of hrs and mins

			if (hrs.matches("[0-9]{1,2}\\.[0-9]{1,2}")) {   // if hours is currently a decimal
				h = Integer.parseInt((hrs.split("\\."))[0]);
				m = (int) ((Float.parseFloat("0."+(hrs.split("\\."))[1]))*60);   // split into hours and minutes
			} else {
				h = Integer.parseInt(hrs);
				m = Integer.parseInt(mins);
			}

			System.out.println("Time found: " + h + " hours and " + m + " minutes");
		}
	

	}

}

*/
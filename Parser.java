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

			stripper.setSortByPosition(true);   // performance implication!
			//stripper.setSpacingTolerance(0.9f);   // doesn't seem to make a difference?
			stripper.setEndPage(1);

			text = stripper.getText(doc).replaceAll("(?m)^[ \t]*\r?\n", "");   // remove empty lines/whitespace

/*			BufferedWriter wr = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(output)));
			stripper.writeText(doc, wr);

			wr.close();*/

		} catch (Exception e) {
			
		} finally {
   			if( doc != null) {
   				try {
    					doc.close();
   				} catch (Exception e) {
   					System.out.println(e.getMessage());
   				}
   			}
   		}

   		System.out.println("----------------------------------------------------------------------------------");

   		Scanner sc = new Scanner(text).useDelimiter("\n");   // iterate over text line by line
   		while (sc.hasNext()) {
   			String next = sc.next().toLowerCase();   // force case insensitivity
   			if (next.matches(".*time.*:\\s*.*")) {   // check if line might contain time details
   				parseTime(next);
   			}
   		}
   		
   		parseTime("time: <insert test case here>".toLowerCase());   // for testing

	}

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
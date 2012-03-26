/***************************************************************************
 * Authors:     J.M. de la Rosa Trevin (jmdelarosa@cnb.csic.es)
 *
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'xmipp@cnb.csic.es'
 ***************************************************************************/

package xmipp.viewer.models;

import ij.ImagePlus;

import java.awt.Dimension;
import java.awt.Image;
import java.awt.Insets;

import javax.swing.JPopupMenu;
import javax.swing.JTable;
import javax.swing.border.Border;
import javax.swing.table.AbstractTableModel;

import xmipp.viewer.ImageDimension;
import xmipp.viewer.ImageItemRenderer;
import xmipp.viewer.windows.ClassesJDialog.ClassInfo;
import xmipp.utils.Cache;
import xmipp.utils.DEBUG;
import xmipp.utils.XmippPopupMenuCreator;

public abstract class ImageGallery extends AbstractTableModel {

	private static final long serialVersionUID = 1L;
	// Store the number of rows and columns
	protected int rows, cols;
	// Total number of elements and last width
	protected int n, last_width;
	// Image original dimensions
	protected int image_width, image_height;
	// Thumbnails dimensions
	protected int thumb_width, thumb_height;
	// Table cell dimensions, this is redundant, but to avoid to be recalculated
	public Dimension cellDim = new Dimension();

	// Relation between real dimensions and thumbnails dimensions
	// scale = image_width / thumb_width
	protected float scale = (float) 1.;
	// protected int zoom = 100;
	// Cache class to reuse of already loaded items
	protected Cache<String, ImageItem> cache = new Cache<String, ImageItem>();
	// Filename
	protected String filename;
	// Hold gallery dimensions
	protected ImageDimension dimension;
	// Renderer to display images
	protected ImageItemRenderer renderer = new ImageItemRenderer();
	// Column model
	protected GalleryColumnModel columnModel;
	// Where to show labels
	// protected boolean showLabel = false;
	// Whether to autoadjust columns
	protected boolean adjustColumns = false;
	// Flags and variables to control global normalization
	protected boolean normalize_calculated = false;
	protected double normalize_min = Double.POSITIVE_INFINITY,
			normalize_max = Double.NEGATIVE_INFINITY;

	public GalleryData data; // information about the gallery

	// Initiazation function
	public ImageGallery(GalleryData data) throws Exception {
		filename = data.filename;
		this.data = data;
		cols = 0;
		dimension = loadDimension();
		columnModel = createColumnModel();
		// Zdim will always be used as number of elements to display
		n = dimension.getZDim();
		image_width = dimension.getXDim();
		image_height = dimension.getYDim();
		setZoomValue(data.zoom);
		// This should be changed later after a call to
		// setColumns or adjustColumns
		if (cols < 1) {
			cols = 1;
			rows = n;
		}
		// DEBUG.printMessage(String.format("col: %d, rows: %d", cols, rows));
		resizeCache();
	}

	// Load initial dimensions
	protected abstract ImageDimension loadDimension() throws Exception;

	/**
	 * Function to create Cache of items calculate the dimension of the cache
	 * depending on images size and available memory
	 */
	protected void resizeCache() {
		int imageSize = dimension.getXDim() * dimension.getYDim()
				* Cache.MAXPXSIZE;
		int elements = Cache.MEMORY_SIZE / imageSize;
		cache.resize(elements > 0 ? elements : 1);
	}

	@Override
	public int getColumnCount() {
		return cols;
	}

	@Override
	public int getRowCount() {
		return rows;
	}

	@Override
	public String getColumnName(int column) {
		return String.format("%d", column + 1);
	}

	@Override
	public Class getColumnClass(int c) {
		return ImageItem.class;
	}

	@Override
	public Object getValueAt(int row, int col) {
		int index = getIndex(row, col);

		if (index < n) {
			try {
				String key = getItemKey(index);
				ImageItem item;
				// If the element is on cache, just return it
				if (cache.containsKey(key))
					item = cache.get(key);
				else {
					// If not, create the item and store it for future
					item = createItem(index, key);
					cache.put(key, item);
				}
				setupItem(item, index);

				return item;
			} catch (Exception e) {
				e.printStackTrace();
			}
		}

		return null;
	}

	protected void setupItem(ImageItem item, int index) {
		ImagePlus imp = item.getImagePlus();
		if (imp != null) { // When image is missing this will be null
			if (data.normalize)
				imp.getProcessor().setMinAndMax(normalize_min, normalize_max);
			else
				imp.getProcessor().resetMinAndMax();
			imp.updateImage();
		}
	}

	public void setRows(int rows) {
		adjustColumns = false;
		if (rows != this.rows) {
			this.rows = rows;
			cols = n / rows + (n % rows == 0 ? 0 : 1);
			fireTableStructureChanged();
		}
	}

	protected void setColumnsValue(int cols) {
		this.cols = cols;
		rows = n / cols + (n % cols == 0 ? 0 : 1);
		fireTableStructureChanged();
	}

	public void setColumns(int cols) {
		adjustColumns = false;
		if (cols != this.cols) {
			setColumnsValue(cols);
		}
	}

	// Return True if columns were changed
	public boolean adjustColumn(int width) {
		last_width = width;
		adjustColumns = true;
		int new_cols = Math.min(width / cellDim.width, n);
		if (new_cols != cols) {
			setColumnsValue(new_cols);
			return true;
		}
		return false;
	}

	public int getSize() {
		return n;
	}

	public Dimension getCellSize() {
		return cellDim;
	}// function getCellSize

	/**
	 * This function will be used to calculate all size need to render the image
	 * cell
	 * 
	 * @param width
	 * @param height
	 */
	protected void calculateCellSize() {
		thumb_width = (int) (image_width * scale);
		thumb_height = (int) (image_height * scale);

		int font_height = 0;
		if (data.showLabel) {
			font_height = renderer.getFontMetrics(renderer.getFont())
					.getHeight();
			font_height += renderer.getIconTextGap(); // Adds the extra gap.
			// font_height -= table.getIntercellSpacing().height; // Removes
		}

		int borderHeight = 0, borderWidth = 0;
		Border border = renderer.getBorder();

		if (border != null) {
			Insets insets = renderer.getBorder().getBorderInsets(renderer);
			borderWidth = insets.left + insets.right;
			borderHeight = insets.bottom + insets.top;
		}
		cellDim.setSize(thumb_width + 1 * borderWidth, thumb_height + 1
				* borderHeight + font_height);
		adjustColumnsWidth();
	}

	/**
	 * This method will be used to set renderers and other table configurations
	 */
	public void setupTable(JTable table) {
		table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
		table.setDefaultRenderer(ImageItem.class, renderer);
	}

	/** Update the table selection according with data selection */
	public void updateTableSelection(JTable table) {
		// For now do nothing, overrided in MetadataTable
	}

	/** Ajust the width of columns and headers */
	protected void adjustColumnsWidth() {
		// renderer.setPreferredSize(cellDim);
		columnModel.setWidth(cellDim.width);
	}

	/** Return the cell renderer to be used to draw images */
	public ImageItemRenderer getRenderer() {
		return renderer;
	}

	/** Return the column model to be used with this table model */
	public GalleryColumnModel getColumnModel() {
		return columnModel;
	}

	/** Internal method to create the column model */
	protected GalleryColumnModel createColumnModel() {
		return new GalleryColumnModel(cellDim.width);
	}

	protected void setZoomValue(int z) {
		data.zoom = z;
		scale = (float) (data.zoom / 100.0);
		calculateCellSize();
	}

	public void setZoom(int z) {
		if (data.zoom != z) {
			setZoomValue(z);
			fireTableDataChanged();
			if (adjustColumns)
				adjustColumn(last_width);
		}
	}

	/**
	 * Calculate index base on x position and y position
	 * 
	 * @param x
	 *            x position on table
	 * @param y
	 *            y position on table
	 * @return index of the element
	 */
	public int getIndex(int row, int col) {
		return row * cols + col;
	}
	
	/** Return the label of the item at this position */
	public abstract String getLabel(int row, int col);

	/**
	 * Return the row and col given an index
	 * 
	 * @param index
	 * @return
	 */
	public int[] getCoords(int index) {
		int[] coords = new int[2];
		coords[0] = index / cols;
		coords[1] = index % cols;
		return coords;
	}

	/** Functions to handle selections */

	/** Set enable/disable to selected items */
	public void setSelectionEnabled(boolean value) {
		try {
			for (int i = 0; i < n; ++i)
				if (data.selection[i])
					data.setEnabled(i, value);
			fireTableDataChanged();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	/** Clear selection list */
	public void clearSelection() {
		for (int i = 0; i < n; ++i)
			data.selection[i] = false;
	}

	/** Select a range of elements given the indexes */
	public void selectRange(int first_index, int last_index, boolean value) {
		for (int i = first_index; i <= last_index; ++i)
			data.selection[i] = value;
		fireTableDataChanged();
	}

	/** Select a range of elements given the coordinates */
	public void selectRange(int first_row, int first_col, int last_row,
			int last_col, boolean value) {
		int i1 = getIndex(first_row, first_col);
		int i2 = getIndex(last_row, last_col);
		int i = Math.min(i1, i2);
		i2 = Math.max(i1, i2);
		for (; i <= i2; ++i)
			data.selection[i] = value;
		fireTableDataChanged();
	}

	/** Set the class of a given selection of elements. */
	public void setSelectionClass(int classNumber) {
		ClassInfo cli = data.getClassInfo(classNumber);
		for (int i = 0; i < n; ++i)
			if (data.selection[i]){
				data.setItemClass(i, cli);
			}
		clearSelection();
		fireTableDataChanged();
	}
	
	/** Remove a class */
	public void removeClass(int classNumber){
		ClassInfo cli = data.getClassInfo(classNumber);
		for (int i = 0; i < n; ++i)
			if (data.getItemClassInfo(i) == cli)
				data.setItemClass(i, null);
		data.classesArray.remove(classNumber);
		fireTableDataChanged();
	}

	/** Set the selection state of an element give row and col */
	public void touchItem(int row, int col) {
		int i = getIndex(row, col);
		data.selection[i] = !data.selection[i];
		fireTableCellUpdated(row, col);
	}

	/**
	 * Goto and select specified item, if there is a selection it will be
	 * cleared
	 */
	public void gotoItem(int i) {
		clearSelection();
		data.selection[i] = !data.selection[i];
		int[] coords = getCoords(i);
		fireTableCellUpdated(coords[0], coords[1]);
	}

	/** Return the number of selected elements */
	public int getSelectedCount() {
		int count = 0;
		for (int i = 0; i < n; ++i)
			if (data.selection[i])
				++count;
		return count;
	}

	/** Normalization utils */
	public void setNormalized(boolean normalize) {

		if (normalize != data.normalize) {
			data.normalize = normalize;
			if (normalize)
				calculateMinAndMax();
			fireTableDataChanged();
		}
	}

	/** Check normalized state */
	public boolean getNormalized() {
		return data.normalize;
	}

	/** Calculate min and max if needed for normalization */
	public void calculateMinAndMax() {
		if (!normalize_calculated) {
			double[] mm = getMinAndMax();
			normalize_min = mm[0];
			normalize_max = mm[1];
			normalize_calculated = true;
		}
	}

	/**
	 * This function will be called when a right click is fired from the UI, the
	 * col and row of cell where the event was produced and also the JPopupMenu
	 * This function will serve to personalize the menu before showing or event
	 * not show at all if the return is false
	 */
	public abstract boolean handleRightClick(int row, int col,
			XmippPopupMenuCreator xpopup);

	/** Whether to display the labels */
	public void setShowLabels(boolean value) {
		if (data.showLabel != value) {
			data.showLabel = value;
			calculateCellSize();
			fireTableDataChanged();
		}
	}

	/** Whether to display the labels */
	public void setRenderImages(boolean value) {
	}

	/** Retrieve the mininum and maximum of data */
	protected abstract double[] getMinAndMax();

	/** Retrieve the image filename, return null if error */
	public abstract String getImageFilenameAt(int row, int col);

	/**
	 * Function to create the key of the item knowing the item index
	 */
	public abstract String getItemKey(int index) throws Exception;
	
	/** Check if the item is busy */
	public boolean isBusy(int row, int col){
		return false;
	}

	/**
	 * Return the main title to be used on windows
	 */
	public abstract String getTitle();

	/**
	 * Return the ImagePlus representation of this gallery
	 */
	public abstract ImagePlus getImagePlus();

	/**
	 * Function to create the image item. this should be implemented in
	 * subclasses of ImageGallery
	 * 
	 * @param index
	 *            The index of the item to create
	 * @return The item created
	 */
	protected abstract ImageItem createItem(int index, String key)
			throws Exception;
	
	/** This class will contains basic info to be used for image rendering.
	 * It will contains an ImagePlus, label and some other useful info.
	 */
	public class ImageItem {
		
		protected ImagePlus image = null;
		protected int index;
		
		/** First argument is the gallery to wich this item belongs
		 * Constructor of ImageItem
		 * @param g gallery to wich this item belongs
		 * @param r row position of the item
		 * @param c 
		 */
		public ImageItem(int row, int col){
			index = ImageGallery.this.getIndex(row, col);
		}
		
		public ImageItem(int index){
			this.index = index;			
		}
		
		public int getIndex(){
			return index;
		}
		
		public ImagePlus getImagePlus() {
			return image;
		}
		
		public void setImagePlus(ImagePlus value){
			image = value;
		}
		
		public Image getImage(){
			if (image != null)
				return image.getImage();
			return null;
		}
		
		public boolean getShowLabel(){
			return data.showLabel;
		}
		
		public Dimension getCellDim(){
			return cellDim;
		}
		
		public String getLabel() {
			int [] coords = getCoords(index);
			return ImageGallery.this.getLabel(coords[0], coords[1]);
		}
		
		public String getKey() {
			try {
				return getItemKey(index);
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			return null;
		}
		
		public boolean isSelected() {
			return data.selection[index];
		}
		
		public boolean isEnabled(){
			return data.isEnabled(index);
		}
		
		public boolean isBusy(){
			int [] coords = getCoords(index);
			return ImageGallery.this.isBusy(coords[0], coords[1]);
		}
		
		public ClassInfo getClassInfo(){
			return data.getItemClassInfo(index);
		}
		
		@Override
		public String toString(){
			return image != null ? 
					image.getFileInfo().fileName: null;
		}
	}//class ImageItem

}

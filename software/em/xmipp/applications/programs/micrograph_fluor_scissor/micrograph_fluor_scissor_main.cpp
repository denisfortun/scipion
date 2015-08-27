/***************************************************************************
 *
 * Authors:     Carlos Oscar S. Sorzano (coss@cnb.csic.es)
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

#include <data/argsparser.h>
#include <data/xmipp_program.h>
#include <data/micrograph.h>
#include <data/args.h>
#include <data/transformations.h>

class ProgMicrographScissor: public XmippProgram
{
private:

protected:
    void defineParams()
    {
    	// ***
        addUsageLine ("Extract particles from a fluorescence micrograph");

        addParamsLine(" == General Options == ");
        addParamsLine("  -i <input_micrograph>               : From which the images will be cutted");
        addParamsLine("  -o <output_stack>                   : Name for the particle images");
        addParamsLine("                                      :+ Two files will be created: output_stack with the particles in a Spider stack an output_stack.xmd with the list of image names, the micrograph they were taken from, and their coordinates");
        addParamsLine("  --pos <position_file>               : file with particle coordinates");

        addParamsLine(" == Processing Options == ");
        addParamsLine("  --Xdim <window_X_dim>               : In pixels");
        addParamsLine("  [--downsampling <float=1.>]         : The positions were determined with this downsampling rate");
        addParamsLine("  [--Ydim <window_Y_dim>]             : If not given Ydim=Xdim");
        addParamsLine("  [--Zdim <window_Z_dim>]             : If not given Zdim=Xdim");
        addParamsLine("  [--XY_sampling <TXY=1>]             : Sampling rate in XY");
        addParamsLine("  [--Z_sampling <TZ=1>]               : Sampling rate in Z");
        addParamsLine("  [--invert]                          : Invert contrast");
        addParamsLine("  [--appendToStack]                   : The output stack is deleted.");
        addParamsLine("                                      : Use this option to add the new images to the stack");
        addParamsLine("  [--compensateZsampling]             : If given, then the Z sampling is set to be the same as the XY");

    	// ***
        addExampleLine ("   xmipp_micrograph_fluor_scissor -i 2DSIM/volumes/2D-SIM_Reconstructed_1_c2.tif --pos SIM2D_centrioles_006.pos  --Xdim 35 --Ydim 35 --Zdim 14 -o particles --compensateZsampling ");
    }
    FileName fn_micrograph,fn_out;
    FileName fn_tilted, fn_out_tilted, fn_angles, fn_tilt_pos;
    FileName fn_orig, fn_pos;
    bool     compensate;
    int      Zdim, Ydim, Xdim;
    bool     reverse_endian;
    bool     compute_inverse ;
    double   down_transform;
    bool     rmStack;

    void readParams()
    {
        fn_micrograph = getParam  ("-i");
        fn_out        = getParam  ("-o");
        fn_pos        = getParam  ("--pos");
        compensate    = checkParam  ("--compensateZsampling");
        Xdim          = getIntParam("--Xdim");
        if (checkParam("--Ydim"))
            Ydim      = getIntParam("--Ydim");
        else
            Ydim = Xdim;
        if (checkParam("--Zdim"))
            Zdim      = getIntParam("--Zdim");
        else
            Zdim = Xdim;
        compute_inverse      = checkParam("--invert");
        rmStack              = !checkParam("--appendToStack");

        down_transform = getDoubleParam("--downsampling");
    }
public:
    void run()
    {
    	std::cout << "************************" << std::endl;
		Image<double> m, particle;
		m.read(fn_micrograph);
		m().setDimensions(XSIZE(m()),YSIZE(m()),NSIZE(m()),1);

		if(Zdim > m().zdim)
			Zdim = m().zdim;

		MetaData positions;
		positions.read(fn_pos);

		size_t idx=0;
		fn_out = fn_out.removeAllExtensions()+".stk";
		if (fileExists(fn_out))
			deleteFile(fn_out);
		int YdimFinal = Ydim;
		int ZdimFinal = Zdim;
		if(compensate)
		{
			YdimFinal = Xdim;
			ZdimFinal = Xdim;
		}
		createEmptyFile(fn_out,Xdim,YdimFinal,ZdimFinal,positions.size(),true);
		MetaData mdOut;
	    FileName fn_aux;
	    size_t ii = 0;
		FOR_ALL_OBJECTS_IN_METADATA(positions)
		{
			int x,y,z;
			positions.getValue(MDL_XCOOR,x,__iter.objId);
			positions.getValue(MDL_YCOOR,y,__iter.objId);
			positions.getValue(MDL_ZCOOR,z,__iter.objId);

			int x0 = x - Xdim/2, y0 = y - Ydim/2;
			int xF = x + Xdim/2 -(1-Xdim%2), yF = y + Ydim/2 -(1-Ydim%2);
			// Take the whole stack
			int z0 = 0;
			int zF = m().zdim;
			m().window(particle(), 0, z0, y0, x0, 0, zF, yF, xF);

			if(compensate)
			{
				particle().setXmippOrigin();
				MultidimArray<double> particle_cubic_data;
				scaleToSize(3,particle_cubic_data,particle.data,Xdim,YdimFinal,ZdimFinal);
				particle.data = particle_cubic_data;
			}

			particle.write(fn_out,++idx,true,WRITE_REPLACE);
			size_t id=mdOut.addObject();
//			mdOut.setValue(MDL_IMAGE,formatString("%d@%s",idx,fn_out.getString().c_str()),id);
            fn_aux.compose(++ii, fn_out);
			mdOut.setValue(MDL_IMAGE,fn_aux,id);
		}
		mdOut.write(fn_out.removeAllExtensions()+".xmd");
    }
};

RUN_XMIPP_PROGRAM(ProgMicrographScissor)

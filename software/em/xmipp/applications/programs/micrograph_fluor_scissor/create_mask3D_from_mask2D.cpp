/***************************************************************************
 *
 * Authors:     Denis Fortun (denis.fortun@epfl.ch)
 *
 * Biomedical Imaging Group, EPFL
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
#include <data/multidim_array.h>

class ProgCreateMask3DFromMask2D: public XmippProgram
{
private:

protected:
    void defineParams()
    {
    	// ***
        addUsageLine ("Extract particles from a fluorescence micrograph");

        addParamsLine(" == General Options == ");
        addParamsLine("  -i <input_2Dmask>                   : 2D mask to expand to 3D");
        addParamsLine("  -o <output_3Dmask>                  : Name for the output mask");

        addParamsLine(" == Processing Options == ");
        addParamsLine("  -zdim <window_X_dim>               : In pixels");
        addParamsLine("  -z0 <window_X_dim>                 : In pixels");
        addParamsLine("  -z1 <window_X_dim>                 : In pixels");

    	// ***
        addExampleLine ("   xmipp_micrograph_fluor_scissor -i 2DSIM/volumes/2D-SIM_Reconstructed_1_c2.tif --pos SIM2D_centrioles_006.pos  --Xdim 35 --Ydim 35 --Zdim 14 -o particles --compensateZsampling ");
    }
    FileName fn_mask2D,fn_out;
    bool     compensate;
    int      zdim,z0,z1;

    void readParams()
    {
        fn_mask2D     = getParam  ("-i");
        fn_out        = getParam  ("-o");
        zdim          = getIntParam  ("-zdim");
        z0            = getIntParam  ("-z0");
        z1            = getIntParam  ("-z1");
    }
public:
    void run()
    {
		std::cout << "////////////////////////////" << std::endl;
		Image<double> mask2D;
		mask2D.read(fn_mask2D);
		std::cout << "000000000000000000000" << std::endl;

		fn_out = fn_out.removeAllExtensions()+".vol";
		if (fileExists(fn_out))
			deleteFile(fn_out);
		createEmptyFile(fn_out,XSIZE(mask2D()),YSIZE(mask2D()),zdim,1,true);

		std::cout << "11111111111111111" << std::endl;
    	MultidimArray<double> ArrayMask3D(zdim,YSIZE(mask2D()),XSIZE(mask2D()));
    	MultidimArray<double> Arraymask2D = mask2D.data;
		for(int z=z0; z<z1; z++)
			ArrayMask3D.setSlice(z,Arraymask2D);
    	Image<double> mask3D(ArrayMask3D);
		std::cout << "2222222222222222" << std::endl;

		fn_out = fn_out.removeAllExtensions()+".vol";
		mask3D.write(fn_out,1,true,WRITE_REPLACE);
		std::cout << "3333333333333333" << std::endl;
    }
};

RUN_XMIPP_PROGRAM(ProgCreateMask3DFromMask2D)

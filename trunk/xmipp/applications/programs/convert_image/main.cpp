/***************************************************************************
 *
 * Authors:    Carlos Oscar            coss@cnb.csic.es (2007)
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

#include <data/args.h>
#include <data/image.h>
#include <data/metadata.h>
#include <data/metadata_extension.h>
#include <data/progs.h>

void Usage();

class progConvImg: public XmippProgram
{
private:
    FileName fn_stack, fn_root, fn_oext, fn_vol, fn_in, fn_out, fn_img;
    std::string type;
    Image<float> in, out;
    MetaData SF;
    MDRow    row;

protected:
    void defineParams()
    {
        addUsageLine("Converts stacks, volumes or images into any of these three elements and any other file format.");
        addParamsLine(" -i <metadata>   :Input file: metadata, stack, volume or image.");
        addParamsLine("         :+ Supported read formats are:");
        addParamsLine("         :+ dm3 : Digital Micrograph 3.");
        addParamsLine("         :+ img : Imagic.");
        addParamsLine("         :+ inf,raw : RAW file with header INF file.");
        addParamsLine("         :+ mrc : CCP4.");
        addParamsLine("         :+ spe : Princeton Instruments CCD camera.");
        addParamsLine("         :+ spi, xmp : Spider.");
        addParamsLine("         :+ tif : TIFF.");
        addParamsLine("         :+ ser : tecnai imaging and analysis-only input");
        addParamsLine("         :+ raw#xDim,yDim,[zDim],offset,datatype,[r] : RAW image file without header file.");
        addParamsLine("         :+ where datatype can be: uchar, char, ushort, short, uint, int, long, float, double, cshort, cint, cfloat, cdouble, bool");
        addParamsLine(" alias --input;");

        addParamsLine("  [-o <output_file=\"\">]  : Output file: metadata, stack, volume or image.");
        addParamsLine("   alias --output;");
        addParamsLine("  [-oext <extension=\"\">] : Output file format extension.");
        addParamsLine("         :+ Supported write formats are:");
        addParamsLine("         :+ img : Imagic");
        addParamsLine("         :+ inf,raw : RAW file with header INF file.");
        addParamsLine("         :+ mrc : CCP4");
        addParamsLine("         :+ spi, xmp : Spider");
        addParamsLine("         :+ tif : TIFF. Supports 8bits, 16bits and float.");
        addParamsLine("  [-oroot <root=\"\">]     : Rootname of output individual images.");
        addParamsLine("[-type <output_type=img>] : Output file type.");
        addParamsLine("          where <output_type>");
        addParamsLine("          img : image");
        addParamsLine("          vol : volume");
        addParamsLine("          stack : stack ");
        addParamsLine("  alias -t;");
    }

    void readParams()
    {
        fn_in = getParam("-i");
        fn_out = getParam("-o");
        fn_oext = getParam("-oext");
        fn_root = getParam("-oroot");

        type = getParam("-type");

        if (!checkParam("-type"))
        {
            if (fn_out.getExtension() == "vol" || fn_oext == "vol")
                type = "vol";
            else if (fn_out.getExtension() == "stk" || fn_oext == "stk")
                type = "stack";
        }


    }
public:
    void run()
    {

        // From metadata to ...............................................
        if (fn_in.isMetaData())
        {
            MetaData SF;
            MDRow    row;
            SF.read(fn_in);
            if (type == "stack")
            {
                FileName fn_stack_plain=fn_stack.removeFileFormat();
                if (exists(fn_stack_plain))
                    unlink(fn_stack_plain.c_str());
                FOR_ALL_OBJECTS_IN_METADATA(SF)
                {
                    FileName fnImg;
                    SF.getValue(MDL_IMAGE,fnImg);
                    SF.getRow(row);
                    in.read(fnImg,true,-1,false,false,&row);
                    in.write(fn_out,-1,true,WRITE_APPEND);
                }
            }
            else if (type == "vol")
            {
                int Xdim, Ydim, Zdim, Ndim;
                ImgSize(SF, Xdim, Ydim, Zdim, Ndim);
                if (Zdim!=1 || Ndim!=1)
                    REPORT_ERROR(ERR_MULTIDIM_DIM,
                                 "Only 2D images can be converted into volumes");
                out().coreAllocate(1,SF.size(),Ydim,Xdim);
                int k=0;
                FOR_ALL_OBJECTS_IN_METADATA(SF)
                {
                    FileName fnImg;
                    SF.getValue(MDL_IMAGE,fnImg);
                    in.read(fnImg);
                    out().setSlice(k++,in());
                }
                out.write(fn_out);
            }
            else if (type == "img")
            {
                fn_root=fn_root.removeFileFormat();
                int k=0;
                MetaData SFout;
                FOR_ALL_OBJECTS_IN_METADATA(SF)
                {
                    FileName fnImg;
                    SF.getValue(MDL_IMAGE,fnImg);
                    SF.getRow(row);
                    in.read(fnImg,true,-1,false,false,&row);
                    FileName fnOut;
                    if (fn_root !="")
                        fnOut.compose(fn_root,k++,fn_oext);
                    else
                        fnOut = (fnImg.withoutExtension()).addExtension(fn_oext);

                    in.write(fnOut);
                    SFout.addObject();
                    SFout.setValue(MDL_IMAGE,fnOut);
                }
                if (fn_root != "")
                    SFout.write(fn_root+".sel");
                else if (fn_out != "")
                    SFout.write(fn_out);
                else
                    SFout.write(fn_in.insertBeforeExtension("_out"));
            }
        }
        else // From Stack file to.....
        {
            in.read(fn_in,false);
            if (NSIZE(in())>1)
            {
                // It's a stack with more than 1 slice
                if (type == "stack")
                {
                    FileName fn_stack_plain=fn_stack.removeFileFormat();
                    if (exists(fn_stack_plain))
                        unlink(fn_stack_plain.c_str());
                    int nmax=NSIZE(in());
                    for (int n=0; n<nmax; n++)
                    {
                        in.read(fn_in,true,n);
                        in.write(fn_out,-1,true,WRITE_APPEND);
                    }
                }
                else if (type == "vol")
                {
                    in.read(fn_in);
                    ZSIZE(in())*=NSIZE(in());
                    NSIZE(in())=1;
                    in.write(fn_out);
                }
                else if (type == "img")
                {
                    fn_root=fn_root.removeFileFormat();
                    MetaData SFout;
                    int nmax=NSIZE(in());
                    for (int n=0; n<nmax; n++)
                    {
                        in.read(fn_in,true,n);
                        FileName fnOut;
                        if (fn_root !="")
                            fnOut.compose(fn_root,n,fn_oext);
                        else
                            fnOut.compose(fn_in.withoutExtension(),n,fn_oext);
                        in.write(fnOut);
                        SFout.addObject();
                        SFout.setValue(MDL_IMAGE,fnOut);
                    }
                    if (fn_root != "")
                        SFout.write(fn_root+".sel");
                    else if (fn_out != "")
                        SFout.write(fn_out);
                    else
                        SFout.write(fn_in.withoutExtension() + "_out.sel");
                }
            }
            else
            {
                // It's a stack with 1 slice, an image or a volume
                in.read(fn_in);
                if (type == "stack")
                {
                    if (ZSIZE(in())>1)
                    {
                        // Convert the volume into a stack
                        NSIZE(in())=ZSIZE(in());
                        ZSIZE(in())=1;
                        int Ndim=NSIZE(in());
                        in.MD.resize(Ndim);
                    }
                    in.write(fn_out,-1,true);
                }
                else if (type == "img" && fn_root!="")
                {
                    fn_root=fn_root.removeFileFormat();
                    MetaData SFout;
                    for (int k=0; k<ZSIZE(in()); k++)
                    {
                        in().getSlice(k,out());
                        FileName fnOut;
                        if (fn_root !="")
                            fnOut.compose(fn_root,k,fn_oext);
                        else
                            fnOut.compose(fn_in.withoutExtension(),k,fn_oext);

                        out.write(fnOut);
                        SFout.addObject();
                        SFout.setValue(MDL_IMAGE,fnOut);
                    }
                    if (fn_root != "")
                        SFout.write(fn_root+".sel");
                    else if (fn_out != "")
                        SFout.write(fn_out);
                    else
                        SFout.write(fn_in.withoutExtension() + "_out.sel");
                }
                else
                    in.write(fn_out);
            }
        }
    }
}
;




int main(int argc, char *argv[])
{


    try
    {
        progConvImg program;
        program.read(argc, argv);
        program.run();
    }
    catch (XmippError xe)
    {
        std::cerr << xe;
    }

    return 0;
}





void oldMain(int argc, char *argv[])
{

    FileName fn_stack, fn_root, fn_vol, fn_in, fn_img;

    // Read arguments --------------------------------------------------------
    try
    {
        fn_in    = getParameter(argc,argv,"-i","");

        fn_stack = getParameter(argc,argv,"-outputStack","");
        fn_root  = getParameter(argc,argv,"-outputRoot","");
        fn_vol   = getParameter(argc,argv,"-outputVol","");
        fn_img   = getParameter(argc,argv,"-outputImg","");
        if (fn_vol=="" && fn_img!="")
            fn_vol=fn_img;

        if (fn_root=="" && fn_stack=="" && fn_vol=="")
            REPORT_ERROR(ERR_ARG_MISSING,"Please, provide one output");
    }
    catch (XmippError XE)
    {
        std::cout << XE;
        Usage();
        exit(1);
    }

    // True work -----------------------------------------------------------
    try
    {
        Image<float> in, out;

        // From metadata to ...............................................
        if (fn_in.isMetaData())
        {
            MetaData SF;
            MDRow    row;
            SF.read(fn_in);
            if (fn_stack!="")
            {
                FileName fn_stack_plain=fn_stack.removeFileFormat();
                if (exists(fn_stack_plain))
                    unlink(fn_stack_plain.c_str());
                FOR_ALL_OBJECTS_IN_METADATA(SF)
                {
                    FileName fnImg;
                    SF.getValue(MDL_IMAGE,fnImg);
                    SF.getRow(row);
                    in.read(fnImg,true,-1,false,false,&row);
                    in.write(fn_stack,-1,true,WRITE_APPEND);
                }
            }
            else if (fn_vol!="")
            {
                int Xdim, Ydim, Zdim, Ndim;
                ImgSize(SF, Xdim, Ydim, Zdim, Ndim);
                if (Zdim!=1 || Ndim!=1)
                    REPORT_ERROR(ERR_MULTIDIM_DIM,
                                 "Only 2D images can be converted into volumes");
                out().coreAllocate(1,SF.size(),Ydim,Xdim);
                int k=0;
                FOR_ALL_OBJECTS_IN_METADATA(SF)
                {
                    FileName fnImg;
                    SF.getValue(MDL_IMAGE,fnImg);
                    in.read(fnImg);
                    out().setSlice(k++,in());
                }
                out.write(fn_vol);
            }
            else if (fn_root!="")
            {
                std::string extension=fn_root.getFileFormat();
                fn_root=fn_root.removeFileFormat();
                int k=0;
                MetaData SFout;
                FOR_ALL_OBJECTS_IN_METADATA(SF)
                {
                    FileName fnImg;
                    SF.getValue(MDL_IMAGE,fnImg);
                    SF.getRow(row);
                    in.read(fnImg,true,-1,false,false,&row);
                    FileName fnOut;
                    fnOut.compose(fn_root,k++,extension);
                    in.write(fnOut);
                    SFout.addObject();
                    SFout.setValue(MDL_IMAGE,fnOut);
                }
                SFout.write(fn_root+".sel");
            }
        }
        else
        {
            in.read(fn_in,false);
            if (NSIZE(in())>1)
            {
                // It's a stack with more than 1 slice
                if (fn_stack!="")
                {
                    FileName fn_stack_plain=fn_stack.removeFileFormat();
                    if (exists(fn_stack_plain))
                        unlink(fn_stack_plain.c_str());
                    int nmax=NSIZE(in());
                    for (int n=0; n<nmax; n++)
                    {
                        in.read(fn_in,true,n);
                        in.write(fn_stack,-1,true,WRITE_APPEND);
                    }
                }
                else if (fn_vol!="")
                {
                    in.read(fn_in);
                    ZSIZE(in())=NSIZE(in());
                    NSIZE(in())=1;
                    in.write(fn_vol);
                }
                else if (fn_root!="")
                {
                    std::string extension=fn_root.getFileFormat();
                    fn_root=fn_root.removeFileFormat();
                    MetaData SFout;
                    int nmax=NSIZE(in());
                    for (int n=0; n<nmax; n++)
                    {
                        in.read(fn_in,true,n);
                        FileName fnOut;
                        fnOut.compose(fn_root,n,extension);
                        in.write(fnOut);
                        SFout.addObject();
                        SFout.setValue(MDL_IMAGE,fnOut);
                    }
                    SFout.write(fn_root+".sel");
                }
            }
            else
            {
                // It's a stack with 1 slice, an image or a volume
                in.read(fn_in);
                if (fn_stack!="")
                {
                    if (ZSIZE(in())>1)
                    {
                        // Convert the volume into a stack
                        NSIZE(in())=ZSIZE(in());
                        ZSIZE(in())=1;
                        int Ndim=NSIZE(in());
                        in.MD.resize(Ndim);
                    }
                    in.write(fn_stack,-1,true);
                }
                else if (fn_vol!="")
                    in.write(fn_vol);
                else if (fn_root!="")
                {
                    std::string extension=fn_root.getFileFormat();
                    fn_root=fn_root.removeFileFormat();
                    MetaData SFout;
                    for (int k=0; k<ZSIZE(in()); k++)
                    {
                        in().getSlice(k,out());
                        FileName fnOut;
                        fnOut.compose(fn_root,k,extension);
                        out.write(fnOut);
                        SFout.addObject();
                        SFout.setValue(MDL_IMAGE,fnOut);
                    }
                    SFout.write(fn_root+".sel");
                }
            }
        }
    }
    catch (XmippError XE)
    {
        std::cout << XE;
    }
    exit(0);
} //main

/* Usage ------------------------------------------------------------------- */
void Usage()
{
    std::cerr << "Purpose:\n";
    std::cerr << "    Converts Spider stacks into images or volumes or any other\n"
    << "    combination of these three elements\n";
    std::cerr << "Usage: convert_image " << std::endl
    << "    -i <filename>                      : Input metadata, stack, volume or image\n"
    << "                                         in any format\n"
    << "   [-outputStack <stackFile>]          : Stack with the set of images\n"
    << "   [-outputRoot <rootname[:format]>]   : Rootname of the individual images\n"
    << "                                       : If no format is provided, spider is assumed\n"
    << "                                         Valid formats are: spi (spider), mrc (ccp4), img (imagic), dm3 (digital micrograph 3-only input), ser (tecnai imaging and analysis-only input) ...\n"
    << "   [-outputVol <volume>]               : Volume with the set of images\n"
    << "   [-outputImg <image>]                : Output image\n"
    ;
}

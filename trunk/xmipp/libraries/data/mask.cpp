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

#include "mask.h"
#include "args.h"
#include "image.h"
#include "volume.h"
#include "wavelet.h"

/*---------------------------------------------------------------------------*/
/* 1D Masks                                                                  */
/*---------------------------------------------------------------------------*/
void RaisedCosineMask(Matrix1D<double> &mask,
                      double r1, double r2, int mode, double x0)
{
    double k = PI / (r2 - r1);
    FOR_ALL_ELEMENTS_IN_MATRIX1D(mask)
    {
        double r = (i - x0);
        if (r <= r1)
            VEC_ELEM(mask, i) = 1;
        else if (r < r2)
            VEC_ELEM(mask, i) = (1 + cos(k * (r - r1))) / 2;
        else
            VEC_ELEM(mask, i) = 0;
        if (mode == OUTSIDE_MASK)
            VEC_ELEM(mask, i) = 1 - VEC_ELEM(mask, i);
    }
}

void RaisedCrownMask(Matrix1D<double> &mask,
                     double r1, double r2, double pix_width, int mode, double x0)
{
    RaisedCosineMask(mask, r1 - pix_width, r1 + pix_width, OUTSIDE_MASK, x0);
    Matrix1D<double> aux;
    aux.resize(mask);
    RaisedCosineMask(aux, r2 - pix_width, r2 + pix_width, INNER_MASK, x0);
    FOR_ALL_ELEMENTS_IN_MATRIX1D(mask)
    {
        VEC_ELEM(mask, i) *= VEC_ELEM(aux, i);
        if (mode == OUTSIDE_MASK)
            VEC_ELEM(mask, i) = 1 - VEC_ELEM(mask, i);
    }
}

void KaiserMask(Matrix1D<double> &mask, double delta, double Deltaw)
{
    // Convert Deltaw from a frequency normalized to 1, to a freq. normalized to PI
    Deltaw *= PI;

    // Design Kaiser window
    double A = -20 * log10(delta);
    double M = CEIL((A - 8) / (2.285 * Deltaw));
    double beta;
    if (A > 50)
        beta = 0.1102 * (A - 8.7);
    else if (A >= 21)
        beta = 0.5842 * pow(A - 21, 0.4) + 0.07886 * (A - 21);
    else
        beta = 0;

    // "Draw" Kaiser window
    mask.resize(2*M + 1);
    mask.setXmippOrigin();
    double iI0Beta = 1.0 / bessi0(beta);
    FOR_ALL_ELEMENTS_IN_MATRIX1D(mask)
    {
        if (ABS(i)<=M)
            mask(i) = bessi0(beta * sqrt(1 - (i / M) * (i / M))) * iI0Beta;
    }
}

void SincMask(Matrix1D<double> &mask,
              double omega, int mode, double x0)
{
    FOR_ALL_ELEMENTS_IN_MATRIX1D(mask)
    {
        double r = ABS(i - x0);
        VEC_ELEM(mask, i) = omega/PI * SINC(omega/PI * r);
        if (mode == OUTSIDE_MASK)
            VEC_ELEM(mask, i) = 1 - VEC_ELEM(mask, i);
    }
}

void SincKaiserMask(Matrix1D<double> &mask,
                    double omega, double delta, double Deltaw)
{
    Matrix1D<double> kaiser;
    KaiserMask(kaiser, delta, Deltaw);
    mask.resize(kaiser);
    mask.setXmippOrigin();
    SincMask(mask, omega*PI, INNER_MASK, 0);
    mask *= kaiser;
}

/*---------------------------------------------------------------------------*/
/* 2D Masks                                                                  */
/*---------------------------------------------------------------------------*/
void BinaryCircularMask(Matrix2D<int> &mask,
                        double radius, int mode, double x0, double y0)
{
    mask.initZeros();
    double radius2 = radius * radius;
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        double r2 = (i - y0) * (i - y0) + (j - x0) * (j - x0);
        if (r2 <= radius2 && mode == INNER_MASK)
            MAT_ELEM(mask, i, j) = 1;
        else if (r2 >= radius2 && mode == OUTSIDE_MASK)
            MAT_ELEM(mask, i, j) = 1;
    }
}

#define DWTCIRCULAR2D_BLOCK(s,quadrant) \
    SelectDWTBlock(s, mask, quadrant, \
                   XX(corner1),XX(corner2),YY(corner1),YY(corner2)); \
    V2_PLUS_V2(center,corner1,corner2); \
    V2_BY_CT(center,center,0.5); \
    FOR_ALL_ELEMENTS_IN_MATRIX2D_BETWEEN(corner1,corner2) { \
        double r2=(XX(r)-XX(center))*(XX(r)-XX(center))+ \
                  (YY(r)-YY(center))*(YY(r)-YY(center)); \
        MAT_ELEM(mask,YY(r),XX(r))=(r2<=radius2); \
    }
void BinaryDWTCircularMask(Matrix2D<int> &mask, double radius,
                           int smin, int smax, const std::string &quadrant)
{
    double radius2 = radius * radius / (4 * (smin + 1));
    mask.initZeros();
    for (int s = smin; s <= smax; s++)
    {
        Matrix1D<int> corner1(2), corner2(2), r(2);
        Matrix1D<double> center(2);
        if (quadrant == "xx")
        {
            DWTCIRCULAR2D_BLOCK(s, "01");
            DWTCIRCULAR2D_BLOCK(s, "10");
            DWTCIRCULAR2D_BLOCK(s, "11");
        }
        else
            DWTCIRCULAR2D_BLOCK(s, quadrant);
        radius2 /= 4;
    }
}

void BinaryCrownMask(Matrix2D<int> &mask,
                     double R1, double R2, int mode, double x0, double y0)
{
    mask.initZeros();
    double R12 = R1 * R1;
    double R22 = R2 * R2;
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        double r2 = (i - y0) * (i - y0) + (j - x0) * (j - x0);
        bool in_crown = (r2 >= R12 && r2 <= R22);
        if (in_crown  && mode == INNER_MASK)
            MAT_ELEM(mask, i, j) = 1;
        else if (!in_crown && mode == OUTSIDE_MASK)
            MAT_ELEM(mask, i, j) = 1;
    }
}

void BinaryFrameMask(Matrix2D<int> &mask,
                     int Xrect, int Yrect, int mode, double x0, double y0)
{
    mask.initZeros();
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        bool in_frame =
            (j >= x0 + FIRST_XMIPP_INDEX(Xrect)) && (j <= x0 + LAST_XMIPP_INDEX(Xrect)) &&
            (i >= y0 + FIRST_XMIPP_INDEX(Yrect)) && (i <= y0 + LAST_XMIPP_INDEX(Yrect));
        if (in_frame  && mode == INNER_MASK)
            MAT_ELEM(mask, i, j) = 1;
        else if (!in_frame && mode == OUTSIDE_MASK)
            MAT_ELEM(mask, i, j) = 1;
    }
}

void GaussianMask(Matrix2D<double> &mask,
                  double sigma, int mode, double x0, double y0)
{
    double sigma2 = sigma * sigma;
    double k = 1 / (sqrt(2 * PI) * sigma);
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        double r2 = (i - y0) * (i - y0) + (j - x0) * (j - x0);
        MAT_ELEM(mask, i, j) = k * exp(-0.5 * r2 / sigma2);
        if (mode == OUTSIDE_MASK)
            MAT_ELEM(mask, i, j) = 1 - MAT_ELEM(mask, i, j);
    }
}

void RaisedCosineMask(Matrix2D<double> &mask,
                      double r1, double r2, int mode, double x0, double y0)
{
    double k = PI / (r2 - r1);
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        double r = sqrt((i - y0) * (i - y0) + (j - x0) * (j - x0));
        if (r <= r1)
            MAT_ELEM(mask, i, j) = 1;
        else if (r < r2)
            MAT_ELEM(mask, i, j) = (1 + cos(k * (r - r1))) / 2;
        else
            MAT_ELEM(mask, i, j) = 0;
        if (mode == OUTSIDE_MASK)
            MAT_ELEM(mask, i, j) = 1 - MAT_ELEM(mask, i, j);
    }
}

void RaisedCrownMask(Matrix2D<double> &mask,
                     double r1, double r2, double pix_width, int mode, double x0, double y0)
{
    RaisedCosineMask(mask, r1 - pix_width, r1 + pix_width, OUTSIDE_MASK, x0, y0);
    Matrix2D<double> aux;
    aux.resize(mask);
    RaisedCosineMask(aux, r2 - pix_width, r2 + pix_width, INNER_MASK, x0, y0);
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        MAT_ELEM(mask, i, j) *= MAT_ELEM(aux, i, j);
        if (mode == OUTSIDE_MASK)
            MAT_ELEM(mask, i, j) = 1 - MAT_ELEM(mask, i, j);
    }
}

void BlackmanMask(Matrix2D<double> &mask, int mode, double x0, double y0)
{
    double Xdim2 = (XSIZE(mask) - 1) * (XSIZE(mask) - 1);
    double Ydim2 = (YSIZE(mask) - 1) * (YSIZE(mask) - 1);
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        double r = sqrt((i - y0) * (i - y0) / Xdim2 + (j - x0) * (j - x0) / Ydim2);
        if (r < 1)
            MAT_ELEM(mask, i, j)  = 0.42 + 0.5 * cos(2 * PI * r) + 0.08 * cos(4 * PI * r);
        else
            MAT_ELEM(mask, i, j)  = 0;
        if (mode == OUTSIDE_MASK)
            MAT_ELEM(mask, i, j) = 1 - MAT_ELEM(mask, i, j);
    }
}

void KaiserMask(Matrix2D<double> &mask, double delta, double Deltaw)
{
    // Convert Deltaw from a frequency normalized to 1, to a freq. normalized to PI
    Deltaw *= PI;

    // Design Kaiser window
    double A = -20 * log10(delta);
    int    M = CEIL((A - 8) / (2.285 * Deltaw));
    double beta;
    if (A > 50)
        beta = 0.1102 * (A - 8.7);
    else if (A >= 21)
        beta = 0.5842 * pow(A - 21, 0.4) + 0.07886 * (A - 21);
    else
        beta = 0;

    // "Draw" Kaiser window
    mask.resize(2*M + 1, 2*M + 1);
    mask.setXmippOrigin();
    double iI0Beta = 1.0 / bessi0(beta);
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        double r = sqrt((double)(i * i + j * j));
        if (r <= M)
            mask(i, j) = bessi0(beta * sqrt(1 - (r / M) * (r / M))) * iI0Beta;
    }
}

void SincMask(Matrix2D<double> &mask,
              double omega, int mode, double x0, double y0)
{
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        double r = sqrt((i - y0) * (i - y0) + (j - x0) * (j - x0));
        MAT_ELEM(mask, i, j) = omega/PI * SINC(omega/PI * r);;
        if (mode == OUTSIDE_MASK)
            MAT_ELEM(mask, i, j) = 1 - MAT_ELEM(mask, i, j);
    }
}

void SincBlackmanMask(Matrix2D<double> &mask,
                      double omega, double power_percentage, int mode, double x0, double y0)
{
    Matrix2D<double> blackman;

#define EVALUATE_POWER_OF_SINCBLACKMAN2D(N,P) \
    mask.resize(N,N); mask.setXmippOrigin(); \
    SincMask(mask,omega,INNER_MASK,x0,y0); \
    blackman.resize(N,N); blackman.setXmippOrigin(); \
    BlackmanMask(blackman); \
    mask *= blackman; \
    P=mask.sum2();

    int N12;
    double P12;
#ifdef NEVER_DEFINED
    // This is a true power percentage estimation, the result is N12
    int N1 = CEIL(100 / omega);
    int N2 = CEIL(1 / omega);
    double P, P1, P2;
    EVALUATE_POWER_OF_SINCBLACKMAN2D(N1, P1);
    P = P1;
    EVALUATE_POWER_OF_SINCBLACKMAN2D(N2, P2);
    power_percentage /= 100;

    // Find size for that power percentage
    bool end = FALSE;
    while (!end)
    {
        std::cout << N1 << " " << P1 << " " << N2 << " " << P2 << std::endl;

        N12 = ROUND((N1 + N2) / 2);
        EVALUATE_POWER_OF_SINCBLACKMAN2D(N12, P12);

        if (ABS(P12 / P - power_percentage) < 0.01)
            end = TRUE;
        else if (N1 == N2 || N1 == N2 + 1)
            end = TRUE;
        else
        {
            if (P12 / P > power_percentage)
            {
                N1 = N12;
                P1 = P12;
            }
            else
            {
                N2 = N12;
                P2 = P12;
            }
        }
    }
#endif

    // And this is an amplitude determination
    N12 = CEIL(1 / omega * CEIL(-1 / 2 + 1 / (PI * (1 - power_percentage / 100))));

    // Create a Sinc mask of that size
    EVALUATE_POWER_OF_SINCBLACKMAN2D(N12, P12);
}

void SincKaiserMask(Matrix2D<double> &mask,
                    double omega, double delta, double Deltaw)
{
    Matrix2D<double> kaiser;
    KaiserMask(kaiser, delta, Deltaw);
    mask.resize(kaiser);
    mask.setXmippOrigin();
    SincMask(mask, omega*PI, INNER_MASK, 0, 0);
    mask *= kaiser;
}

void SeparableSincKaiserMask(Matrix2D<double> &mask,
                             double omega, double delta, double Deltaw)
{
    // Convert Deltaw from a frequency normalized to 1, to a freq. normalized to PI
    Deltaw *= PI;
    omega *= PI;

    // Design Kaiser window
    double A = -20 * log10(delta);
    double M = CEIL((A - 8) / (2.285 * Deltaw));
    double beta;
    if (A > 50)
        beta = 0.1102 * (A - 8.7);
    else if (A >= 21)
        beta = 0.5842 * pow(A - 21, 0.4) + 0.07886 * (A - 21);
    else
        beta = 0;

    // "Draw" Separable Kaiser Sinc window
    mask.resize(2*M + 1, 2*M + 1);
    mask.setXmippOrigin();
    double iI0Beta = 1.0 / bessi0(beta);
    FOR_ALL_ELEMENTS_IN_MATRIX2D(mask)
    {
        mask(i, j) = omega/PI * SINC(omega/PI * i) * omega/PI * SINC(omega/PI * j) *
                     bessi0(beta * sqrt((double)(1 - (i / M) * (i / M)))) * iI0Beta *
                     bessi0(beta * sqrt((double)(1 - (j / M) * (j / M)))) * iI0Beta;
    }
}

void mask2D_4neig(Matrix2D<int> &mask, int value, int center)
{
    mask.resize(3, 3);
    mask.initZeros();
    mask(0, 1) = mask(1, 0) = mask(1, 2) = mask(2, 1) = value;
    mask(1, 1) = center;

}
void mask2D_8neig(Matrix2D<int> &mask, int value1, int value2, int center)
{
    mask.resize(3, 3);
    mask.initZeros();
    mask(0, 1) = mask(1, 0) = mask(1, 2) = mask(2, 1) = value1;
    mask(0, 0) = mask(0, 2) = mask(2, 0) = mask(2, 2) = value2;
    mask(1, 1) = center;

}

/*---------------------------------------------------------------------------*/
/* 3D Masks                                                                  */
/*---------------------------------------------------------------------------*/
void BinarySphericalMask(Matrix3D<int> &mask,
                         double radius, int mode, double x0, double y0, double z0)
{
    mask.initZeros();
    double radius2 = radius * radius;
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double r2 = (k - z0) * (k - z0) + (i - y0) * (i - y0) + (j - x0) * (j - x0);
        if (r2 <= radius2 && mode == INNER_MASK)
            VOL_ELEM(mask, k, i, j) = 1;
        else if (r2 >= radius2 && mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1;
    }
}

#define DWTSPHERICALMASK_BLOCK(s,quadrant) \
    SelectDWTBlock(s, mask, quadrant, \
                   XX(corner1),XX(corner2),YY(corner1),YY(corner2), \
                   ZZ(corner1),ZZ(corner2)); \
    V3_PLUS_V3(center,corner1,corner2); \
    V3_BY_CT(center,center,0.5); \
    FOR_ALL_ELEMENTS_IN_MATRIX3D_BETWEEN(corner1,corner2) { \
        double r2=(XX(r)-XX(center))*(XX(r)-XX(center))+ \
                  (YY(r)-YY(center))*(YY(r)-YY(center))+ \
                  (ZZ(r)-ZZ(center))*(ZZ(r)-ZZ(center)); \
        VOL_ELEM(mask,ZZ(r),YY(r),XX(r))=(r2<=radius2); \
    }
void BinaryDWTSphericalMask(Matrix3D<int> &mask, double radius,
                            int smin, int smax, const std::string &quadrant)
{
    mask.initZeros();
    double radius2 = radius * radius / (4 * (smin + 1));
    for (int s = smin; s <= smax; s++)
    {
        Matrix1D<int> corner1(3), corner2(3), r(3);
        Matrix1D<double> center(3);
        if (quadrant == "xxx")
        {
            DWTSPHERICALMASK_BLOCK(s, "001");
            DWTSPHERICALMASK_BLOCK(s, "010");
            DWTSPHERICALMASK_BLOCK(s, "011");
            DWTSPHERICALMASK_BLOCK(s, "100");
            DWTSPHERICALMASK_BLOCK(s, "101");
            DWTSPHERICALMASK_BLOCK(s, "110");
            DWTSPHERICALMASK_BLOCK(s, "111");
        }
        else
            DWTSPHERICALMASK_BLOCK(s, quadrant);
        radius2 /= 4;
    }
}

void BinaryCrownMask(Matrix3D<int> &mask,
                     double R1, double R2, int mode, double x0, double y0, double z0)
{
    mask.initZeros();
    double R12 = R1 * R1;
    double R22 = R2 * R2;
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double r2 = (k - z0) * (k - z0) + (i - y0) * (i - y0) + (j - x0) * (j - x0);
        int in_crown = (r2 >= R12 && r2 <= R22);
        if (in_crown  && mode == INNER_MASK)
            VOL_ELEM(mask, k, i, j) = 1;
        else if (!in_crown && mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1;
    }
}

void BinaryCylinderMask(Matrix3D<int> &mask,
                        double R, double H, int mode, double x0, double y0, double z0)
{
    mask.initZeros();
    double R2 = R * R;
    double H_2 = H / 2;
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double r2 = (i - y0) * (i - y0) + (j - x0) * (j - x0);
        int in_cyilinder = (r2 <= R2 && ABS(k - z0) <= H_2);
        if (in_cyilinder  && mode == INNER_MASK)
            VOL_ELEM(mask, k, i, j) = 1;
        else if (!in_cyilinder && mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1;
    }
}

void BinaryFrameMask(Matrix3D<int> &mask,
                     int Xrect, int Yrect, int Zrect, int mode, double x0, double y0, double z0)
{
    mask.initZeros();
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        bool in_frame =
            (j >= x0 + FIRST_XMIPP_INDEX(Xrect)) && (j <= x0 + LAST_XMIPP_INDEX(Xrect)) &&
            (i >= y0 + FIRST_XMIPP_INDEX(Yrect)) && (i <= y0 + LAST_XMIPP_INDEX(Yrect)) &&
            (k >= z0 + FIRST_XMIPP_INDEX(Zrect)) && (k <= z0 + LAST_XMIPP_INDEX(Zrect));
        if (in_frame  && mode == INNER_MASK)
            VOL_ELEM(mask, k, i, j) = 1;
        else if (!in_frame && mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1;
    }
}

void BinaryConeMask(Matrix3D<int> &mask, double theta, int mode)
{

    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double rad = tan(PI * theta / 180.) * (double)k;
        if ((double)(i*i + j*j) < rad*rad)
            VOL_ELEM(mask, k, i, j) = 0;
        else
            VOL_ELEM(mask, k, i, j) = 1;
        if (mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1 - VOL_ELEM(mask, k, i, j);
    }

}

void BinaryWedgeMask(Matrix3D<double> &mask, double theta0, double thetaF,
                     Matrix2D<double> A)
{

    double xp, yp, zp;
    double tg0, tgF, limx0, limxF;

    tg0 = -tan(PI * (-90. - thetaF) / 180.);
    tgF = -tan(PI * (90. - theta0) / 180.);

    A = A.inv();
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        xp = dMij(A, 0, 0) * (double)j + dMij(A, 0, 1) * (double)i + dMij(A, 0, 2) * (double)k;
        zp = dMij(A, 2, 0) * (double)j + dMij(A, 2, 1) * (double)i + dMij(A, 2, 2) * (double)k;
        limx0 = tg0 * zp;
        limxF = tgF * zp;
        if (zp >= 0)
        {
            if (xp <= limx0 || xp >= limxF)
                VOL_ELEM(mask, k, i, j) = 1.;
            else
                VOL_ELEM(mask, k, i, j) = 0.;
        }
        else
        {
            if (xp <= limxF || xp >= limx0)
                VOL_ELEM(mask, k, i, j) = 1.;
            else
                VOL_ELEM(mask, k, i, j) = 0.;
        }
    }

}

void GaussianMask(Matrix3D<double> &mask,
                  double sigma, int mode, double x0, double y0, double z0)
{
    double sigma2 = sigma * sigma;
    double K = 1 / sqrt(2 * PI * sigma);
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double r2 = (k - z0) * (k - z0) + (i - y0) * (i - y0) + (j - x0) * (j - x0);
        VOL_ELEM(mask, k, i, j) = K * exp(-0.5 * r2 / sigma2);
        if (mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1 - VOL_ELEM(mask, k, i, j);
    }
}

void RaisedCosineMask(Matrix3D<double> &mask,
                      double r1, double r2, int mode, double x0, double y0, double z0)
{
    double K = PI / (r2 - r1);
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double r = sqrt((k - z0) * (k - z0) + (i - y0) * (i - y0) + (j - x0) * (j - x0));
        if (r <= r1)
            VOL_ELEM(mask, k, i, j) = 1;
        else if (r < r2)
            VOL_ELEM(mask, k, i, j) = (1 + cos(K * (r - r1))) / 2;
        else
            VOL_ELEM(mask, k, i, j) = 0;
        if (mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1 - VOL_ELEM(mask, k, i, j);
    }
}

void RaisedCrownMask(Matrix3D<double> &mask,
                     double r1, double r2, double pix_width, int mode, double x0, double y0,
                     double z0)
{
    RaisedCosineMask(mask, r1 - pix_width, r1 + pix_width, OUTSIDE_MASK, x0, y0, z0);
    Matrix3D<double> aux;
    aux.resize(mask);
    RaisedCosineMask(aux, r2 - pix_width, r2 + pix_width, INNER_MASK, x0, y0, z0);
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        VOL_ELEM(mask, k, i, j) *= VOL_ELEM(aux, k, i, j);
        if (mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1 - VOL_ELEM(mask, k, i, j);
    }
}

void BlobCircularMask(Matrix3D<double> &mask,
                      double r1, blobtype blob,
                      int mode, double x0, double y0, double z0)
{
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double r = sqrt((k - z0) * (k - z0) + (i - y0) * (i - y0) + (j - x0) * (j - x0));
        if (mode == INNER_MASK)
        {
            if (r <= r1)
                VOL_ELEM(mask, k, i, j) = 1;
            else
                VOL_ELEM(mask, k, i, j) = blob_val(r-r1, blob);
        }
        else
        {
            if (r >= r1)
                VOL_ELEM(mask, k, i, j) = 1;
            else
                VOL_ELEM(mask, k, i, j) = blob_val(r1-r, blob);
        }
    }

}
void BlobCrownMask(Matrix3D<double> &mask,
                   double r1, double r2, blobtype blob,
                   int mode, double x0, double y0, double z0)
{
    Matrix3D<double> aux;
    aux.resize(mask);
    if (mode == INNER_MASK)
    {
        BlobCircularMask(mask, r1, blob,
                         OUTSIDE_MASK, x0, y0, z0);
        BlobCircularMask(aux, r2, blob,
                         INNER_MASK, x0, y0, z0);
        FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
        {
            VOL_ELEM(mask, k, i, j) *= VOL_ELEM(aux, k, i, j);
        }
    }
    else
    {
        BlobCircularMask(mask, r1, blob,
                         INNER_MASK, x0, y0, z0);
        BlobCircularMask(aux, r2, blob,
                         OUTSIDE_MASK, x0, y0, z0);
        FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
        {
            VOL_ELEM(mask, k, i, j) += VOL_ELEM(aux, k, i, j);
        }
    }

}

void BlackmanMask(Matrix3D<double> &mask, int mode, double x0, double y0,
                  double z0)
{
    double Xdim2 = (XSIZE(mask) - 1) * (XSIZE(mask) - 1);
    double Ydim2 = (YSIZE(mask) - 1) * (YSIZE(mask) - 1);
    double Zdim2 = (ZSIZE(mask) - 1) * (ZSIZE(mask) - 1);
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double r = sqrt((k - z0) * (k - z0) / Zdim2 + (i - y0) * (i - y0) / Xdim2 + (j - x0) * (j - x0) / Ydim2);
        VOL_ELEM(mask, k, i, j) = 0.42 + 0.5 * cos(2 * PI * r) + 0.08 * cos(4 * PI * r);
        if (mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1 - VOL_ELEM(mask, k, i, j);
    }
}

void SincMask(Matrix3D<double> &mask,
              double omega, int mode, double x0, double y0, double z0)
{
    FOR_ALL_ELEMENTS_IN_MATRIX3D(mask)
    {
        double r = sqrt((k - z0) * (k - z0) + (i - y0) * (i - y0) + (j - x0) * (j - x0));
        VOL_ELEM(mask, k, i, j) = omega/PI * SINC(omega/PI * r);;
        if (mode == OUTSIDE_MASK)
            VOL_ELEM(mask, k, i, j) = 1 - VOL_ELEM(mask, k, i, j);
    }
}

void SincBlackmanMask(Matrix3D<double> &mask,
                      double omega, double power_percentage, int mode, double x0, double y0,
                      double z0)
{
    Matrix3D<double> blackman;

#define EVALUATE_POWER_OF_SINCBLACKMAN3D(N,P) \
    mask.resize(N,N,N); mask.setXmippOrigin(); \
    SincMask(mask,omega,INNER_MASK,x0,y0,z0); \
    blackman.resize(N,N,N); blackman.setXmippOrigin(); \
    BlackmanMask(blackman); \
    mask *= blackman; \
    P=mask.sum2();

    int N12;
    double P12;
    N12 = CEIL(1 / omega * CEIL(-1 / 2 + 1 / (PI * (1 - power_percentage / 100))));
    EVALUATE_POWER_OF_SINCBLACKMAN3D(N12, P12);
}

void mask3D_6neig(Matrix3D<int> &mask, int value, int center)
{
    mask.resize(3, 3, 3);
    mask.initZeros();
    mask(1, 1, 1) = center;
    mask(1, 1, 0) = mask(1, 1, 2) = mask(0, 1, 1) = mask(2, 1, 1) = mask(1, 0, 1) = mask(1, 2, 1) = value;

}

void mask3D_18neig(Matrix3D<int> &mask, int value1, int value2, int center)
{
    mask.resize(3, 3, 3);
    mask.initZeros();
    mask(1, 1, 1) = center;
    //Face neighbors
    mask(1, 1, 0) = mask(1, 1, 2) = mask(0, 1, 1) = mask(2, 1, 1) = mask(1, 0, 1) = mask(1, 2, 1) = value1;
    //Edge neighbors
    mask(0, 1, 0) = mask(0, 0, 1) = mask(0, 1, 2) = mask(0, 2, 1) = value2;
    mask(1, 0, 0) = mask(1, 2, 0) = mask(1, 0, 2) = mask(1, 2, 2) = value2;
    mask(2, 1, 0) = mask(2, 0, 1) = mask(2, 1, 2) = mask(2, 2, 1) = value2;


}
void mask3D_26neig(Matrix3D<int> &mask, int value1, int value2, int value3,
                   int center)
{
    mask.resize(3, 3, 3);
    mask.initZeros();
    mask(1, 1, 1) = center;
    //Face neighbors
    mask(1, 1, 0) = mask(1, 1, 2) = mask(0, 1, 1) = mask(2, 1, 1) = mask(1, 0, 1) = mask(1, 2, 1) = value1;
    //Edge neighbors
    mask(0, 1, 0) = mask(0, 0, 1) = mask(0, 1, 2) = mask(0, 2, 1) = value2;
    mask(1, 0, 0) = mask(1, 2, 0) = mask(1, 0, 2) = mask(1, 2, 2) = value2;
    mask(2, 1, 0) = mask(2, 0, 1) = mask(2, 1, 2) = mask(2, 2, 1) = value2;
    //Vertex neighbors
    mask(0, 0, 0) = mask(0, 0, 2) = mask(0, 2, 0) = mask(0, 2, 2) = value3;
    mask(2, 0, 0) = mask(2, 0, 2) = mask(2, 2, 0) = mask(2, 2, 2) = value3;

}

/*---------------------------------------------------------------------------*/
/* Mask Type                                                                 */
/*---------------------------------------------------------------------------*/
// Constructor -------------------------------------------------------------
Mask_Params::Mask_Params(int _allowed_data_types)
{
    clear();
    allowed_data_types = _allowed_data_types;
}

// Default values ----------------------------------------------------------
void Mask_Params::clear()
{
    type = NO_MASK;
    mode = INNER_MASK;
    H = R1 = R2 = sigma = 0;
    imask1D.clear();
    imask2D.clear();
    imask3D.clear();
    dmask1D.clear();
    dmask2D.clear();
    dmask3D.clear();
    allowed_data_types = 0;
    fn_mask = "";
    x0 = y0 = z0 = 0;
}

// Resize ------------------------------------------------------------------
void Mask_Params::resize(int Xdim)
{
    switch (datatype())
    {
    case INT_MASK:
        imask1D.resize(Xdim);
        imask1D.setXmippOrigin();
        break;
    case DOUBLE_MASK:
        dmask1D.resize(Xdim);
        dmask1D.setXmippOrigin();
        break;
    }
}

void Mask_Params::resize(int Ydim, int Xdim)
{
    switch (datatype())
    {
    case INT_MASK:
        imask2D.resize(Ydim, Xdim);
        imask2D.setXmippOrigin();
        break;
    case DOUBLE_MASK:
        dmask2D.resize(Ydim, Xdim);
        dmask2D.setXmippOrigin();
        break;
    }
}

void Mask_Params::resize(int Zdim, int Ydim, int Xdim)
{
    switch (datatype())
    {
    case INT_MASK:
        imask3D.resize(Zdim, Ydim, Xdim);
        imask3D.setXmippOrigin();
        break;
    case DOUBLE_MASK:
        dmask3D.resize(Zdim, Ydim, Xdim);
        dmask3D.setXmippOrigin();
        break;
    }
}

// Read from command lines -------------------------------------------------
void Mask_Params::read(int argc, char **argv)
{
    int i = paremeterPosition(argc, argv, "-center");
    if (i != -1)
    {
        if (i + 3 >= argc)
            REPORT_ERROR(1, "Mask: Not enough parameters after -center");
        x0 = textToFloat(argv[i+1]);
        y0 = textToFloat(argv[i+2]);
        z0 = textToFloat(argv[i+3]);
    }
    else
    {
        x0 = y0 = z0 = 0;
    }

    i = paremeterPosition(argc, argv, "-mask");
    if (i == -1)
    {
        clear();
        return;
    }
    if (i + 1 >= argc)
        REPORT_ERROR(3000, "Mask_Params: -mask with no mask_type");
    // Circular mask ........................................................
    if (strcmp(argv[i+1], "circular") == 0)
    {
        if (i + 2 >= argc)
            REPORT_ERROR(3000, "Mask_Params: circular mask with no radius");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: binary masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        if (R1 < 0)
        {
            mode = INNER_MASK;
            R1 = ABS(R1);
        }
        else if (R1 > 0)
            mode = OUTSIDE_MASK;
        else
            REPORT_ERROR(3000, "Mask_Params: circular mask with radius 0");
        type = BINARY_CIRCULAR_MASK;
        // Circular DWT mask ....................................................
    }
    else if (strcmp(argv[i+1], "DWT_circular") == 0)
    {
        if (i + 5 >= argc)
            REPORT_ERROR(3000, "Mask_Params: DWT circular mask with not enough parameters");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: binary masks are not allowed");
        R1 = ABS(textToFloat(argv[i+2]));
        smin = textToInteger(argv[i+3]);
        smax = textToInteger(argv[i+4]);
        quadrant = argv[i+5];
        type = BINARY_DWT_CIRCULAR_MASK;
        // Rectangular mask .....................................................
    }
    else if (strcmp(argv[i+1], "rectangular") == 0)
    {
        if (i + 3 >= argc)
            REPORT_ERROR(3000, "Mask_Params: rectangular mask needs at least two dimensions");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: binary masks are not allowed");
        Xrect = textToInteger(argv[i+2]);
        Yrect = textToInteger(argv[i+3]);
        if (i + 4 < argc)
        {
            Zrect = textToInteger(argv[i+4]);
            if (argv[i+4][0] != '-')
                Zrect = ABS(Zrect);
        }
        else
            Zrect = 0;
        if (Xrect < 0 && Yrect < 0 && Zrect <= 0)
        {
            mode = INNER_MASK;
            Xrect = ABS(Xrect);
            Yrect = ABS(Yrect);
            Zrect = ABS(Zrect);
        }
        else if (Xrect > 0 && Yrect > 0 && Zrect >= 0)
            mode = OUTSIDE_MASK;
        else
            REPORT_ERROR(3000, "Mask_Params: cannot determine mode for rectangle");
        type = BINARY_FRAME_MASK;
        // Cone mask ............................................................
    }
    else if (strcmp(argv[i+1], "cone") == 0)
    {
        if (i + 2 >= argc)
            REPORT_ERROR(3000, "Mask_Params: cone mask needs one angle");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: binary masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        if (R1 < 0)
        {
            mode = INNER_MASK;
            R1 = ABS(R1);
        }
        else
            mode = OUTSIDE_MASK;
        type = BINARY_CONE_MASK;
        // Wedge mask ............................................................
    }
    else if (strcmp(argv[i+1], "wedge") == 0)
    {
        if (i + 3 >= argc)
            REPORT_ERROR(3000, "Mask_Params: wedge mask needs two angles");
        if (!(allowed_data_types & DOUBLE_MASK))
            REPORT_ERROR(3000, "Mask_Params: binary masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        R2 = textToFloat(argv[i+3]);
        type = BINARY_WEDGE_MASK;
        // Crown mask ...........................................................
    }
    else if (strcmp(argv[i+1], "crown") == 0)
    {
        if (i + 3 >= argc)
            REPORT_ERROR(3000, "Mask_Params: crown mask needs two radii");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: binary masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        R2 = textToFloat(argv[i+3]);
        if (R1 < 0 && R2 < 0)
        {
            mode = INNER_MASK;
            R1 = ABS(R1);
            R2 = ABS(R2);
        }
        else if (R1 > 0 && R2 > 0)
            mode = OUTSIDE_MASK;
        else
            REPORT_ERROR(3000, "Mask_Params: cannot determine mode for crown");
        type = BINARY_CROWN_MASK;
        // Cylinder mask ........................................................
    }
    else if (strcmp(argv[i+1], "cylinder") == 0)
    {
        if (i + 3 >= argc)
            REPORT_ERROR(3000, "Mask_Params: cylinder mask needs a radius and a height");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: binary masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        H = textToFloat(argv[i+3]);
        if (R1 < 0 && H < 0)
        {
            mode = INNER_MASK;
            R1 = ABS(R1);
            H = ABS(H);
        }
        else if (R1 > 0 && H > 0)
            mode = OUTSIDE_MASK;
        else
            REPORT_ERROR(3000, "Mask_Params: cannot determine mode for cylinder");
        type = BINARY_CYLINDER_MASK;
        // Gaussian mask ........................................................
    }
    else if (strcmp(argv[i+1], "gaussian") == 0)
    {
        if (i + 2 >= argc)
            REPORT_ERROR(3000, "Mask_Params: gaussian mask needs a sigma");
        if (!(allowed_data_types & DOUBLE_MASK))
            REPORT_ERROR(3000, "Mask_Params: continuous masks are not allowed");
        sigma = textToFloat(argv[i+2]);
        if (sigma < 0)
        {
            mode = INNER_MASK;
            sigma = ABS(sigma);
        }
        else
            mode = OUTSIDE_MASK;
        type = GAUSSIAN_MASK;
        // Raised cosine mask ...................................................
    }
    else if (strcmp(argv[i+1], "raised_cosine") == 0)
    {
        if (i + 3 >= argc)
            REPORT_ERROR(3000, "Mask_Params: raised_cosine mask needs two radii");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: continuous masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        R2 = textToFloat(argv[i+3]);
        if (R1 < 0 && R2 < 0)
        {
            mode = INNER_MASK;
            R1 = ABS(R1);
            R2 = ABS(R2);
        }
        else if (R1 > 0 && R2 > 0)
            mode = OUTSIDE_MASK;
        else
            REPORT_ERROR(3000, "Mask_Params: cannot determine mode for raised_cosine");
        type = RAISED_COSINE_MASK;
        // Raised crown mask ....................................................
    }
    else if (strcmp(argv[i+1], "raised_crown") == 0)
    {
        if (i + 4 >= argc)
            REPORT_ERROR(3000, "Mask_Params: raised_crown mask needs two radii & a width");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: continuous masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        R2 = textToFloat(argv[i+3]);
        pix_width = textToFloat(argv[i+4]);
        if (R1 < 0 && R2 < 0)
        {
            mode = INNER_MASK;
            R1 = ABS(R1);
            R2 = ABS(R2);
        }
        else if (R1 > 0 && R2 > 0)
            mode = OUTSIDE_MASK;
        else
            REPORT_ERROR(3000, "Mask_Params: cannot determine mode for raised_cosine");
        type = RAISED_CROWN_MASK;
        // Blob circular mask ....................................................
    }
    else if (strcmp(argv[i+1], "blob_circular") == 0)
    {
        if (i + 3 >= argc)
            REPORT_ERROR(3000, "Mask_Params: blob_circular mask needs one radius and a width");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: continuous masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        double aux = textToFloat(argv[i+3]);
        blob_radius= ABS(aux);
        if (aux < 0)
            mode = INNER_MASK;
        else if (aux > 0)
            mode = OUTSIDE_MASK;
        else
            REPORT_ERROR(3000, "Mask_Params: cannot determine mode for blob_circular");
        type = BLOB_CIRCULAR_MASK;
        blob_order= textToFloat(getParameter(argc, argv, "-m", "2."));
        blob_alpha= textToFloat(getParameter(argc, argv, "-a", "10.4"));

        // Raised crown mask ....................................................
    }
    else if (strcmp(argv[i+1], "blob_crown") == 0)
    {
        if (i + 4 >= argc)
            REPORT_ERROR(3000, "Mask_Params: blob_crown mask needs two radii and a with");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: continuous masks are not allowed");
        R1 = textToFloat(argv[i+2]);
        R2 = textToFloat(argv[i+3]);
        double aux = textToFloat(argv[i+4]);
        blob_radius= ABS(aux);
        if (aux < 0)
            mode = INNER_MASK;
        else if (aux > 0)
            mode = OUTSIDE_MASK;
        else
            REPORT_ERROR(3000, "Mask_Params: cannot determine mode for blob_crown");
        type = BLOB_CROWN_MASK;
        blob_order= textToFloat(getParameter(argc, argv, "-m", "2."));
        blob_alpha= textToFloat(getParameter(argc, argv, "-a", "10.4"));

        // Blackman mask ........................................................
    }
    else if (strcmp(argv[i+1], "blackman") == 0)
    {
        mode = INNER_MASK;
        type = BLACKMAN_MASK;
        // Sinc mask ............................................................
    }
    else if (strcmp(argv[i+1], "sinc") == 0)
    {
        if (i + 2 >= argc)
            REPORT_ERROR(3000, "Mask_Params: sinc mask needs a frequency");
        if (!(allowed_data_types & INT_MASK))
            REPORT_ERROR(3000, "Mask_Params: binary masks are not allowed");
        omega = textToFloat(argv[i+2]);
        if (omega < 0)
        {
            mode = INNER_MASK;
            omega = ABS(omega);
        }
        else
            mode = OUTSIDE_MASK;
        type = SINC_MASK;
    }
    else
    {
        fn_mask = argv[i+1];
        type = READ_MASK;
    }
}

// Show --------------------------------------------------------------------
void Mask_Params::show() const
{
#define SHOW_MODE \
    if (mode==INNER_MASK) std::cout << "   mode=INNER MASK\n"; \
    else                  std::cout << "   mode=OUTER MASK\n";
#define SHOW_CENTER \
    std::cout << "   (x0,y0,z0)=(" << x0 << "," << y0 << "," << z0 << ")\n";
    switch (type)
    {
    case NO_MASK:
        std::cout << "Mask type: No mask\n";
        break;
    case BINARY_CIRCULAR_MASK:
        std::cout << "Mask type: Binary circular\n"
                  << "   R=" << R1 << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case BINARY_DWT_CIRCULAR_MASK:
        std::cout << "Mask type: Binary DWT circular\n"
                  << "   R=" << R1 << std::endl
                  << "   smin=" << smin << std::endl
                  << "   smax=" << smax << std::endl
                  << "   quadrant=" << quadrant << std::endl;
        break;
    case BINARY_CROWN_MASK:
        std::cout << "Mask type: Binary crown\n"
                  << "   R1=" << R1 << std::endl
                  << "   R2=" << R2 << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case BINARY_CYLINDER_MASK:
        std::cout << "Mask type: Cylinder\n"
                  << "   R1=" << R1 << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case BINARY_FRAME_MASK:
        std::cout << "Mask type: Frame\n"
                  << "   Xrect=" << Xrect << std::endl
                  << "   Yrect=" << Yrect << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case GAUSSIAN_MASK:
        std::cout << "Mask type: Gaussian\n"
                  << "   sigma=" << sigma << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case RAISED_COSINE_MASK:
        std::cout << "Mask type: Raised cosine\n"
                  << "   R1=" << R1 << std::endl
                  << "   R2=" << R2 << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case RAISED_CROWN_MASK:
        std::cout << "Mask type: Raised crown\n"
                  << "   R1=" << R1 << std::endl
                  << "   R2=" << R2 << std::endl
                  << "   pixwidth=" << pix_width << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case BLOB_CIRCULAR_MASK:
        std::cout << "Mask type: Blob circular\n"
                  << "   R1=" << R1 << std::endl
                  << "   blob radius=" << blob_radius << std::endl
                  << "   blob order="  << blob_order  << std::endl
                  << "   blob alpha="  << blob_alpha  << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case BLOB_CROWN_MASK:
        std::cout << "Mask type: Blob crown\n"
                  << "   R1=" << R1 << std::endl
                  << "   R2=" << R2 << std::endl
                  << "   blob radius=" << blob_radius << std::endl
                  << "   blob order="  << blob_order  << std::endl
                  << "   blob alpha="  << blob_alpha  << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case BLACKMAN_MASK:
        std::cout << "Mask type: Blackman\n";
        SHOW_MODE;
        SHOW_CENTER;
        break;
    case SINC_MASK:
        std::cout << "Mask type: Sinc\n"
                  << "   w=" << omega << std::endl;
        SHOW_MODE;
        SHOW_CENTER;
        break;
    default:
        std::cout << "Mask type: Read from disk\n"
                  << "   File=" << fn_mask << std::endl;
        break;
    }
}

// Usage -------------------------------------------------------------------
void Mask_Params::usage() const
{
    std::cerr << "Mask usage:\n";
    std::cerr << "   [-center <x0=0> <y0=0> <z0=0>]: Center of the mask\n";
    if (allowed_data_types & INT_MASK)
        std::cerr << "   [-mask circular <R>       : circle/sphere mask\n"
                  << "                               if R>0 => outside R\n"
                  << "                               if R<0 => inside  R\n"
                  << "   [-mask DWT_circular <R> <smin> <smax>: circle/sphere mask\n"
                  << "                               smin and smax define the scales\n"
                  << "                               to be kept\n"
                  << "   |-mask rectangular <Xrect> <Yrect> [<Zrect>]: 2D or 3D rectangle\n"
                  << "                               if X,Y,Z > 0 => outside rectangle\n"
                  << "                               if X,Y,Z < 0 => inside rectangle\n"
                  << "   |-mask crown <R1> <R2>    : 2D or 3D crown\n"
                  << "                               if R1,R2 > 0 => outside crown\n"
                  << "                               if R1,R2 < 0 => inside crown\n"
                  << "   |-mask cylinder <R> <H>   : 2D circle or 3D cylinder\n"
                  << "                               if R,H > 0 => outside cylinder\n"
                  << "                               if R,H < 0 => inside cylinder\n"
                  << "   |-mask cone <theta>       : 3D cone (parallel to Z) \n"
                  << "                               if theta > 0 => outside cone\n"
                  << "                               if theta < 0 => inside cone\n"
                  << "   |-mask wedge <th0> <thF>  : 3D missing-wedge mask for data \n"
                  << "                               collected between tilting angles \n"
                  << "                               th0 and thF (around the Y-axis) \n"
                  << "   |-mask <binary file>      : Read from file\n"
                  ;
    if (allowed_data_types & DOUBLE_MASK)
        std::cerr << "   |-mask gaussian <sigma>   : 2D or 3D gaussian\n"
                  << "                               if sigma > 0 => outside gaussian\n"
                  << "                               if sigma < 0 => inside gaussian\n"
                  << "   |-mask raised_cosine <R1> <R2>: 2D or 3D raised_cosine\n"
                  << "                               if R1,R2 > 0 => outside sphere\n"
                  << "                               if R1,R2 < 0 => inside sphere\n"
                  << "   |-mask raised_crown <R1> <R2> <pixwidth>: 2D or 3D raised_crown\n"
                  << "                               if R1,R2 > 0 => outside sphere\n"
                  << "                               if R1,R2 < 0 => inside sphere\n"
                  << "   |-mask blob_circular <R1> <blob_radius>: 2D or 3D blob circular\n"
                  << "                               if blob_radius > 0 => outside sphere\n"
                  << "                               if blob_radius < 0 => inside sphere\n"
                  << "   |-mask blob_crown <R1> <R2> <blob_radius>: 2D or 3D blob_crown\n"
                  << "                               if blob_radius > 0 => outside sphere\n"
                  << "                               if blob_radius < 0 => inside sphere\n"
                  << "   [ -m <blob_order=2>       : Order of blob\n"
                  << "   [ -a <blob_alpha=10.4>    : Alpha of blob\n"
                  << "   |-mask blackman           : 2D or 3D Blackman mask\n"
                  << "                               always inside blackman\n"
                  << "   |-mask sinc <w>]          : 2D or 3D sincs\n"
                  << "                               if w > 0 => outside sinc\n"
                  << "                               if w < 0 => inside sinc\n"
                  ;
}

// Write -------------------------------------------------------------------
void Mask_Params::write_1Dmask(const FileName &fn)
{
    if (datatype() == INT_MASK)
        imask2D.write(fn);
    else if (datatype() == DOUBLE_MASK)
        dmask2D.write(fn);
}

void Mask_Params::write_2Dmask(const FileName &fn)
{
    ImageXmipp I;
    if (datatype() == INT_MASK)
        I = imask2D;
    else if (datatype() == DOUBLE_MASK)
        I = dmask2D;
    I.write(fn);
}

void Mask_Params::write_3Dmask(const FileName &fn)
{
    VolumeXmipp V;
    if (datatype() == INT_MASK)
        V = imask3D;
    else if (datatype() == DOUBLE_MASK)
        V = dmask3D;
    V.write(fn);
}

// Generate 1D mask --------------------------------------------------------
void Mask_Params::generate_1Dmask()
{
    switch (type)
    {
    case NO_MASK:
        imask2D.initConstant(1);
        break;
    case RAISED_COSINE_MASK:
        RaisedCosineMask(dmask1D, R1, R2, mode, x0);
        break;
    case RAISED_CROWN_MASK:
        RaisedCrownMask(dmask1D, R1, R2, pix_width, mode, x0);
        break;
    case READ_MASK:
        imask2D.read(fn_mask);
        imask2D.setXmippOrigin();
        break;
    default:
        REPORT_ERROR(3000, "Mask_Params::generate_mask: Non implemented or "
                     "unknown mask type :" + integerToString(type));
    }
}

// Generate 2D mask --------------------------------------------------------
void Mask_Params::generate_2Dmask(const bool& apply_geo)
{
    ImageXmipp I;
    switch (type)
    {
    case NO_MASK:
        imask2D.initConstant(1);
        break;
    case BINARY_CIRCULAR_MASK:
        BinaryCircularMask(imask2D, R1, mode, x0, y0);
        break;
    case BINARY_DWT_CIRCULAR_MASK:
        BinaryDWTCircularMask(imask2D, R1, smin, smax, quadrant);
        break;
    case BINARY_CROWN_MASK:
        BinaryCrownMask(imask2D, R1, R2, mode, x0, y0);
        break;
    case BINARY_CYLINDER_MASK:
        BinaryCircularMask(imask2D, R1, mode, x0, y0);
        break;
    case BINARY_FRAME_MASK:
        BinaryFrameMask(imask2D, Xrect, Yrect, mode, x0, y0);
        break;
    case GAUSSIAN_MASK:
        GaussianMask(dmask2D, sigma, mode, x0, y0);
        break;
    case RAISED_COSINE_MASK:
        RaisedCosineMask(dmask2D, R1, R2, mode, x0, y0);
        break;
    case RAISED_CROWN_MASK:
        RaisedCrownMask(dmask2D, R1, R2, pix_width, mode, x0, y0);
        break;
    case BLACKMAN_MASK:
        BlackmanMask(dmask2D, mode, x0, y0);
        break;
    case SINC_MASK:
        SincMask(dmask2D, omega, mode, x0, y0);
        break;
    case READ_MASK:
        I.read(fn_mask);
        typeCast(I(), imask2D);
        imask2D.setXmippOrigin();
        break;
    default:
        REPORT_ERROR(3000, "Mask_Params::generate_mask: Unknown mask type :"
                     + integerToString(type));
    }

    if (apply_geo)
    {
        switch (datatype())
        {
        case INT_MASK:
            apply_geo_binary_2D_mask(imask2D, mask_geo);
            break;
        case DOUBLE_MASK:
            apply_geo_cont_2D_mask(dmask2D, mask_geo);
            break;
        }
    }
}

// Generate 3D mask --------------------------------------------------------
void Mask_Params::generate_3Dmask()
{
    VolumeXmipp V;
    Matrix2D<double> AA(4, 4);
    blobtype blob;
    if (type==BLOB_CIRCULAR_MASK || type==BLOB_CROWN_MASK)
    {
        blob.radius = blob_radius;
        blob.order = blob_order;
        blob.alpha = blob_alpha;
    }
    AA.initIdentity();
    switch (type)
    {
    case NO_MASK:
        imask3D.initConstant(1);
        break;
    case BINARY_CIRCULAR_MASK:
        BinarySphericalMask(imask3D, R1, mode, x0, y0, z0);
        break;
    case BINARY_DWT_CIRCULAR_MASK:
        BinaryDWTSphericalMask(imask3D, R1, smin, smax, quadrant);
        break;
    case BINARY_CROWN_MASK:
        BinaryCrownMask(imask3D, R1, R2, mode, x0, y0, z0);
        break;
    case BINARY_CYLINDER_MASK:
        BinaryCylinderMask(imask3D, R1, H, mode, x0, y0, z0);
        break;
    case BINARY_FRAME_MASK:
        BinaryFrameMask(imask3D, Xrect, Yrect, Zrect, mode, x0, y0, z0);
        break;
    case BINARY_CONE_MASK:
        BinaryConeMask(imask3D, R1, mode);
        break;
    case BINARY_WEDGE_MASK:
        BinaryWedgeMask(dmask3D, R1, R2, AA);
        break;
    case GAUSSIAN_MASK:
        GaussianMask(dmask3D, sigma, mode, x0, y0, z0);
        break;
    case RAISED_COSINE_MASK:
        RaisedCosineMask(dmask3D, R1, R2, mode, x0, y0, z0);
        break;
    case RAISED_CROWN_MASK:
        RaisedCrownMask(dmask3D, R1, R2, pix_width, mode, x0, y0, z0);
        break;
    case BLOB_CIRCULAR_MASK:
        BlobCircularMask(dmask3D, R1, blob, mode, x0, y0, z0);
        break;
    case BLOB_CROWN_MASK:
        BlobCrownMask(dmask3D, R1, R2, blob, mode, x0, y0, z0);
        break;
    case BLACKMAN_MASK:
        BlackmanMask(dmask3D, mode, x0, y0, z0);
        break;
    case SINC_MASK:
        SincMask(dmask3D, omega, mode, x0, y0, z0);
        break;
    case READ_MASK:
        V.read(fn_mask);
        typeCast(V(), imask3D);
        imask3D.setXmippOrigin();
        break;
    default:
        REPORT_ERROR(3000, "Mask_Params::generate_mask: Unknown mask type :"
                     + integerToString(type));
    }
}

/*---------------------------------------------------------------------------*/
/* Mask tools                                                                */
/*---------------------------------------------------------------------------*/

// Apply geometric transformation to a binary mask ========================
void apply_geo_binary_2D_mask(Matrix2D<int> &mask,
                              const Matrix2D<double> &A)
{
    Matrix2D<double> tmp;
    tmp.resize(mask);
    typeCast(mask, tmp);
    double outside = DIRECT_MAT_ELEM(tmp, 0, 0);
    // Instead of IS_INV for images use IS_NOT_INV for masks!
    tmp.selfApplyGeometry(A, IS_NOT_INV, DONT_WRAP, outside);
    // The type cast gives strange results here, using round instead
    //typeCast(tmp, mask);
    FOR_ALL_DIRECT_ELEMENTS_IN_MATRIX2D(mask)
    {
        dMij(mask,i,j)=ROUND(dMij(tmp,i,j));
    }
}

// Apply geometric transformation to a continuous mask =====================
void apply_geo_cont_2D_mask(Matrix2D<double> &mask,
                            const Matrix2D<double> &A)
{
    double outside = DIRECT_MAT_ELEM(mask, 0, 0);
    // Instead of IS_INV for images use IS_NOT_INV for masks!
    mask.selfApplyGeometry(A, IS_NOT_INV, DONT_WRAP, outside);
}

// Count with mask =========================================================
int count_with_mask(const Matrix2D<int> &mask,
                    const Matrix2D< std::complex<double> > &m, int mode, double th1, double th2)
{
    SPEED_UP_temps;
    int N = 0;
    FOR_ALL_ELEMENTS_IN_COMMON_IN_MATRIX2D(mask, m)
    if (MAT_ELEM(mask, i, j))
        switch (mode)
        {
        case (COUNT_ABOVE):
            if (abs(MAT_ELEM(m, i, j)) >= th1)
                N++;
            break;
        case (COUNT_BELOW):
            if (abs(MAT_ELEM(m, i, j)) <= th1)
                N++;
            break;
        case (COUNT_BETWEEN):
            if (abs(MAT_ELEM(m, i, j)) >= th1 && abs(MAT_ELEM(m, i, j)) <= th2)
                N++;
            break;
        }
    return N;
}

int count_with_mask(const Matrix3D<int> &mask,
                    const Matrix3D< std::complex<double> > &m, int mode, double th1, double th2)
{
    SPEED_UP_temps;
    int N = 0;
    FOR_ALL_ELEMENTS_IN_COMMON_IN_MATRIX3D(mask, m)
    if (MAT_ELEM(mask, i, j))
        switch (mode)
        {
        case (COUNT_ABOVE):
            if (abs(VOL_ELEM(m, k, i, j)) >= th1)
                N++;
            break;
        case (COUNT_BELOW):
            if (abs(VOL_ELEM(m, k, i, j)) <= th1)
                N++;
            break;
        case (COUNT_BETWEEN):
            if (abs(VOL_ELEM(m, k, i, j)) >= th1 && abs(VOL_ELEM(m, k, i, j)) <= th2)
                N++;
            break;
        }
    return N;
}

/* Range adjust ------------------------------------------------------------ */
void rangeAdjust_within_mask(const Matrix2D<double> *mask,
                             const Matrix2D<double> &m1,
                             Matrix2D<double> &m2)
{
    Matrix2D<double> A(2, 2);
    A.initZeros();
    Matrix1D<double> b(2);
    b.initZeros();
    SPEED_UP_temps;
    // Compute Least squares solution
    if (mask == NULL)
    {
        FOR_ALL_ELEMENTS_IN_COMMON_IN_MATRIX2D(m1, m2)
        {
            A(0, 0) += m2(i, j) * m2(i, j);
            A(0, 1) += m2(i, j);
            A(1, 1) += 1;
            b(0)   += m1(i, j) * m2(i, j);
            b(1)   += m1(i, j);
        }
        A(1, 0) = A(0, 1);
    }
    else
    {
        FOR_ALL_ELEMENTS_IN_COMMON_IN_MATRIX2D(*mask, m2)
        {
            if ((*mask)(i, j))
            {
                A(0, 0) += m2(i, j) * m2(i, j);
                A(0, 1) += m2(i, j);
                A(1, 1) += 1;
                b(0)   += m1(i, j) * m2(i, j);
                b(1)   += m1(i, j);
            }
        }
        A(1, 0) = A(0, 1);
    }
    b = A.inv() * b;

    // Apply to m2
    FOR_ALL_ELEMENTS_IN_MATRIX2D(m2) m2(i, j) = b(0) * m2(i, j) + b(1);
}

void rangeAdjust_within_mask(const Matrix3D<double> *mask,
                             const Matrix3D<double> &m1, Matrix3D<double> &m2)
{
    Matrix2D<double> A(2, 2);
    A.initZeros();
    Matrix1D<double> b(2);
    b.initZeros();
    SPEED_UP_temps;
    // Compute Least squares solution
    if (mask == NULL)
    {
        FOR_ALL_ELEMENTS_IN_COMMON_IN_MATRIX3D(m1, m2)
        {
            A(0, 0) += m2(k, i, j) * m2(k, i, j);
            A(0, 1) += m2(k, i, j);
            A(1, 1) += 1;
            b(0)   += m1(k, i, j) * m2(k, i, j);
            b(1)   += m1(k, i, j);
        }
        A(1, 0) = A(0, 1);
    }
    else
    {
        FOR_ALL_ELEMENTS_IN_COMMON_IN_MATRIX3D(*mask, m2)
        {
            if ((*mask)(k, i, j))
            {
                A(0, 0) += m2(k, i, j) * m2(k, i, j);
                A(0, 1) += m2(k, i, j);
                A(1, 1) += 1;
                b(0)   += m1(k, i, j) * m2(k, i, j);
                b(1)   += m1(k, i, j);
            }
        }
        A(1, 0) = A(0, 1);
    }
    b = A.inv() * b;

    // Apply to m2
    FOR_ALL_ELEMENTS_IN_MATRIX3D(m2) m2(k, i, j) = b(0) * m2(k, i, j) + b(1);
}

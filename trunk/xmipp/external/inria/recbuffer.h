/*
 * Copyright INRIA
 * Author Gregoire Malandain (greg@sophia.inria.fr)
 * Date: June, 9 1998
 */
/*
 * recursive filtering of a buffer (a [1,2,3]D array)
 * according that the filtering is separable
 */

#ifndef _recbuffer_h_
#define _recbuffer_h_

#ifdef __cplusplus
extern "C"
{
#endif /* __cplusplus */

#include <stdio.h>
#ifndef HAVE_MALLOC_H
#include <stdlib.h>
#else
#include <malloc.h>
#endif
#include "typedefs.h"
#include "convert.h"
#include "recline.h"


    /* Recursive filtering on 3D buffers.
     *
     * DESCRIPTION:
     * Performs recursive filtering on 3D buffers.
     * Each direction (X, Y or Z) is performed
     * independently (separability).
     *
     * A direction is filtered if there are enough
     * points along this direction (at least 5),
     * if the coefficient along this direction is
     * positive, and if the derivative's order along
     * this direction is not NODERIVATIVE (see
     * derivativeOrder).
     *
     * Once a line along a direction is extracted for
     * filtering, one may want to add points at both
     * ends of the line to avoid cut-off effects. The
     * value of each endpoint is repeated n times.
     * Thus the length of the line is increased by
     * 2*n.
     *
     * PARAMETERS:
     *
     * - bufferDims[0] is the dimension along X,
     *
     *   bufferDims[1] is the dimension along Y,
     *
     *   bufferDims[2] is the dimension along Y.
     *
     * - borderLengths[0] is the number of points to be
     *   added at both ends of each X line (if
     *   positive). The value of each endpoint is
     *   repeated borderLengths[0] times to produce
     *   a line of length
     *   bufferDims[0] + 2 * borderLengths[0].
     *
     *   borderLengths[1] is the number of points to be
     *   added at both ends of each Y line.
     *
     *   borderLengths[2] is the number of points to be
     *   added at both ends of each Z line.
     *
     * - derivatives[0] is the order of the derivative
     *   to be computed along direction X.
     *
     *   derivatives[1] is the order of the derivative
     *   to be computed along direction Y.
     *
     *   derivatives[2] is the order of the derivative
     *   to be computed along direction Z.
     *
     * - filterCoefs[0] is the coefficient of the filter
     *   to be applied along direction X.
     *
     *   filterCoefs[1] is the coefficient of the filter
     *   to be applied along direction Y.
     *
     *   filterCoefs[2] is the coefficient of the filter
     *   to be applied along direction Z.
     *
     * - filterType is the type of recursive filter to
     *   be applied to the 3D buffer.
     *
     * RETURN:
     *
     * - 0 in case of error
     *
     * - 1 if successful
     *
     * SEE ALSO:
     *
     * - bufferType.
     *
     * - derivativeOrder.
     *
     * - recursiveFilterType.
     *
     * - InitRecursiveCoefficients
     */
    extern int RecursiveFilterOnBuffer(void *bufferIn, /* input buffer */
                                       bufferType typeIn, /* type of the input buffer */
                                       void *bufferOut, /* output buffer */
                                       bufferType typeOut, /* type of the output buffer */
                                       int *bufferDims, /* buffers' dimensions */
                                       int *borderLengths, /* number of points to be added at both ends */
                                       derivativeOrder *derivatives, /* order of derivatives to be computed */
                                       float *filterCoefs, /* coefficients of the filters to be applied */
                                       recursiveFilterType filterType /* type of the recursive filter to be applied */
                                      );



    /* Turn on verbose mode.
     *
     * DESCRIPTION:
     * Some information will be written on stderr when processing.
     * It will turn on the verbose mode of recline too, by
     * calling Recline_verbose();
     */
    extern void Recbuffer_verbose();



    /* Turn off verbose mode.
     *
     * DESCRIPTION:
     * Nothing will be written on stderr when processing.
     * Exactly the contrary of Recbuffer_verbose ().
     * It will turn off the verbose mode of recline too.
     */
    extern void Recbuffer_noverbose();


#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* _recbuffer_h_ */

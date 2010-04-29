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
#ifndef _PROG_RECONS_TEST_HH
#define _PROG_RECONS_TEST_HH

#include <vector>

#include <data/funcs.h>

#include "foms_evaluate.h"

/**@defgroup Recons_test phantom_test_reconstruction (Test of the full reconstruction process)
   @ingroup ReconsLibraryPrograms */
//@{
/* Test parameters --------------------------------------------------------- */
/// Recons_test Parameters
class Recons_test_Parameters
{
public:
    /// Random phantom description filename
    FileName fn_random_phantom;

    /// Phantom volume in voxels
    FileName fn_voxel_phantom;

    /// Projection parameters filename
    FileName fn_proj_params;

    /// Crystal parameters
    FileName fn_crystal;

    /// Symemtry file. Included while ART process
    FileName fn_sym;

    /// Do not use symproj
    bool     do_not_use_symproj;

    /// Force symmetry
    int      force_sym;

    /// Final symmetry file. At the end of the reconstruction process
    FileName fn_final_sym;

    /// CTF to apply
    FileName fn_CTF;

    /// Defocus change
    double   defocus_change;

    /// noise power before CTF
    double sigma;

    /// Lowpass filter noise before CTF
    double low_pass_before_CTF;

    /// High pass filter cutoff
    double w_hp;

#define use_ART         1
#define use_SIRT        2
#define use_WBP         3
#define use_SIRT_Spider 4
#define use_FOURIER     5
    /** Reconstruction mode: use_ART, use_SIRT, use_WBP, use_SIRT_Spider or
        use_FOURIER */
    int recons_method;

    /// Random sort of projections (TRUE or FALSE)?
    bool random_sort;

    /// Sort with last N. If -1, with all previous
    int sort_last_N;

    /// Initial Relaxation parameter (valid for ART and SIRT)
    std::vector<double> lambda0;

    /// Final Relaxation parameter (valid for ART and SIRT)
    std::vector<double> lambdaF;

    /// Initial Number of iterations (valid for ART and SIRT)
    std::vector<int> no_it0;

    /// Final Number of iterations (valid for ART and SIRT)
    std::vector<int> no_itF;

    /// Use succesive relaxation parameters
    bool succesive_params;

    /// Threshold for WBP
    std::vector<double> WBP_threshold;

    /// Padding for the projections (Fourier reconstruction)
    int pad_proj;

    /// Padding for the volume (Fourier reconstruction)
    int pad_vol;

    /// Maximum expected resolution (<1/2), used to filter reconstruction
    double max_resolution;

    /** Number of tests to be considered a measure.
        If it is -1 then it is not used and the accuracy goals are
        used instead, but this goal is only valid for training */
    int MeasNo;

    /** Accuracy for the measures (%).
        We want the true value of the FOM to be within a (%) of the
        measured value. Typical value 2. We can have an unlucky
        random selection with
        a probability determined by the next variable. If it is -1
        then the measure number is used instead of this criterion.
        This option is only valid for training */
    float accuracy;

    /** Admitted unluckiness.
        Probability with which we admit an unlucky selection of samples.
        Typical value 0.01, that means that 1 of every 100 trials we
        will have a measure which is not within a 2% of the true value. */
    float unluckiness;

    // True if only structural consistency should be evaluated.
    // This value is set by the single measure functions. Programmer
    // should not care about it
    int only_structural;

    /// Global radius for evaluation
    double global_radius;

    /// Probe radius for surface generation
    double probe_radius;
    /// Enable top surface
    bool enable_top_surface;
    /// Surface top range
    double top0;
    /// Surface top range
    double topF;

    /// Enable bottom surface
    bool enable_bottom_surface;
    /// Surface bottom range
    double bottom0;
    /// Surface bottom range
    double bottomF;

    /// Surface generation by thresholding
    bool enable_segmented_surface;
    /// Threshold for surface generation
    double threshold_surface_segment;
    /// Dilation amount for surface and starting volume generation
    int    segmented_dilation;

    /// Start from phantom
    bool start_from_phantom;

    /// Starting filter (in digital freq.)
    double starting_low_pass;

    /// Starting noise
    double starting_noise;

    /// Mass constraint
    double mass;

    /// Reconstruct also without any constraint
    bool run_also_without_constraints;

#define BIG_BLOB 1
#define SMALL_BLOB 2
#define VISUAL_BLOB 3
    /// Blob type = BIG_BLOB, SMALL_BLOB or VISUAL BLOB
    int blob_type;
    /// True if voxel basis
    bool voxel_basis;
    /// Stop at = Number of images after which the algorithm must stop
    int stop_at;
    /// Apply positivity
    bool POCS_positivity;
    /// Reconstruction radius
    double reconstruction_radius;

    /** Enable normalization. The following parameters are useless if this
        flag is off */
    bool enable_normalization;

    /// Average of a in y=ax+b
    double a_avg;
    /// Stddev of a in y=ax+b
    double a_stddev;
    /// Average of b in y=ax+b
    double b_avg;
    /// Stddev of b in y=ax+b
    double b_stddev;
    /// Normalizing method. See \ref Normalize_parameters
    int normalizing_method;
    /// Background radius
    int bg_radius;

    /// Correct CTF phase
    bool correct_phase;
    /// Correct amplitude via IDR
    bool correct_amplitude;
    /// IDR relaxation factor
    double mu;
    /// Unmatched CTF correction
    bool unmatched;

    /// Tomography
    bool tomography;

    /// Evaluate
    bool evaluate;
    /** Phantom for evaluation.
        Should be empty if it is the same as the projected phantom. */
    FileName fn_alternative_evaluation_phantom;
    /// Smooth mask before evaluation
    FileName fn_smooth_evaluation_mask;
public:
    /** Read parameters from file. */
    void read(const FileName &fn_test_params);

    /** Show parameters */
    friend std::ostream & operator << (std::ostream &out, const Recons_test_Parameters
                                       &prm);
};

/** Single measure on a FOM.
    A measure is compound of \ref Recons_test_Parameters::MeasNo tests.
    This function returns the mean and standard deviation of all tests
    on the selected FOM. Parameter i is the
    index to bu used inside the (lambda, no_it) list, i can be 0 if
    the reconstruction method is WBP. The results for the last test
    are returned.
    The parameter nvol is used to generate different images and volumes
    for different experiments. It must start with value 1 and internally
    is increased. If you set it to -1 then this option is not used and
    volumes from different experiments are all written with the same
    name.

    training_N contains the number of samples used for tFOM approximation,
    if prm.MeasNo is different from -1, then training_N=prm.MeasNo. Else,
    the number of samples is dynamically calcultaed for the accuracy selected

    Valid FOMs: scL1, scL11, scL10, scL2, scL21, scL20, scL1w, scL2w*/
void single_measure_on_FOM(Recons_test_Parameters &prm,
                           int i, int &nvol,
                           double &training_mean, double &training_stddev, double &training_N,
                           EVALUATE_results &results, const std::string &training_FOM);

/** Single measure on all FOMs.
    A measure is compound of \ref Recons_test_Parameters::MeasNo tests.
    This function returns the mean and standard deviation of all tests
    over all FOMs. Parameter i is the
    index to bu used inside the (lambda, no_it) list, i can be 0 if
    the reconstruction method is WBP. The results for the last test
    are returned.
    The parameter nvol is used to generate different images and volumes
    for different experiments. It must start with value 1 and internally
    is increased. If you set it to -1 then this option is not used and
    volumes from different experiments are all written with the same
    name.*/
void single_measure_on_all_FOMs(Recons_test_Parameters &prm, int i,
                                int &nvol, FOMs &foms_mean, FOMs &foms_stddev, EVALUATE_results &results);

/** Single reconstruction test.
    This function performs a whole reconstruction process, starting from
    generating a random phantom, a set of projections, reconstructing
    and then evaluating it. All evaluation results are returned in the
    EVALUATE_results structure. In the case of SIRT and ART the index i
    indicates which (lambda,no_it) combination is taken from
    the list.

    If the projection root name is g0tA, this function generates the
    following files and using nvol:
    @code
    g0tAexp<nvol>_.descr --> Random phantom generated
    g0tAexp<nvol>_*      --> Projections
    g0tAexp<nvol>_.sel   --> Selection file for the projections
    g0tAexp<nvol>_.vol   --> reconstruction
    @endcode
    and without using nvol:
    @code
    g0tA.descr           --> Random phantom generated
    g0tA*                --> Projections
    g0tA.sel             --> Selection file for the projections
    g0tA.vol             --> reconstruction
    @endcode

    In the case of SIRT of Spider a Spider batch file (b73.xmp) is created,
    and the convention of names are
    */
void single_recons_test(const Recons_test_Parameters &prm,
                        int i, int nvol, EVALUATE_results &results);
//@}
#endif

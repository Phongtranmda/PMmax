# Preparing and publishing PMmax on GitHub

## 1. Current status

The repository includes installation and usage instructions, data specifications, Python dependencies, reproducibility notes, citation metadata, an MIT license, Git configuration, issue and pull request templates, and automated repository checks. Both original scripts retain their names. Tool 2 now uses `mmax_prediction.py` to fix inconsistent feature names within saved stacking models; include this module when publishing or copying the software. Training logic and saved model weights are unchanged. The public repository is https://github.com/Phongtranmda/PMmax. Source code and supplied example data, trained models, maps, figures, evaluation workbooks and logs are published; no versioned release is claimed.

**Software author and copyright holder:** Tran Van Phong.

**Affiliation:** Institute of Earth Sciences, Vietnam Academy of Science and Technology.

**Contact:** tvphong@ies.vast.vn.

The associated manuscript is being prepared for submission to *Computers & Geosciences* and has not yet been published. The root `CITATION.cff` records the software author without inventing a paper DOI or publication details.

PMmax is a provisional name based on the working directory. Complete the following before publication:

- Confirm the official software name and add other software authors, if applicable.
- Add the manuscript title; update its status and DOI when available. Software can be released before the paper is published.
- Add the repository URL, release version and actual release date.
- Confirm data redistribution rights; the software copyright holder has already selected MIT.
- Document predictor sources, units and category codes, and the construction and magnitude scale of the Mmax target.
- Record the successful execution environment and comparisons with manuscript results.

Do not present a draft containing unresolved placeholders as a completed release.

## 2. Licensing and citation

A software license defines how others may use the source code. It is not a permit required to write or run Python. GitHub does not require every repository to have a license, but making code public does not automatically grant general reuse, modification and redistribution rights. The journal requires a clear license. See [GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

MIT permits use, modification and distribution, including commercial use, provided that copyright and license notices are retained. It does not transfer copyright ownership or require recipients to disclose their modifications. Requests to cite the software or paper belong in README and CITATION; MIT does not itself require academic citation. See [the MIT license](https://choosealicense.com/licenses/mit/).

The copyright holder has selected MIT. The root `LICENSE` contains the full license with `Copyright (c) 2026 Tran Van Phong`; README and CITATION reflect this choice. Applying MIT requires no registration, fee or approval from MIT: distribute the license with the source code. This is software licensing, not copyright registration. `docs/LICENSE-MIT.template` remains a reference template. Establish data-sharing terms separately; do not assume the software license covers all input data.

Update `CITATION.cff` with verified information. Use `docs/CITATION.cff.template` only as a reference for missing fields. Add any additional authors, repository URL, version, release date and DOI when available. Keep README consistent and remove preparation notices when the corresponding work is complete.

## 3. Large data and model files

GitHub blocks files larger than 100 MiB in regular Git repositories; browser uploads have a 25 MiB limit. See [GitHub's large-file documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

Locally, `Sample_area.txt` contains 2,027,395,256 bytes and `Stacking.pkl` contains 160,623,466 bytes. The full mapping input, models, results and logs are included as example artifacts; original local files remain intact. Git LFS tracks the mapping input, `*.pkl` models and `*.tif` maps.

Git LFS is configured for the large example artifacts. Use `git lfs pull` after cloning to retrieve them. A separate persistent research archive or DOI may be added later. Do not force large artifacts into regular Git.

Add download links, licenses, checksums and restoration paths to `docs/DATA.md`. For example, generate SHA-256 checksums in PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'Example data/Sample_area.txt'
Get-FileHash -Algorithm SHA256 -LiteralPath 'Example data/EQ_sample_Mmax.xlsx'
```

The synthetic mapping example checks the export interface; it does not reproduce scientific results. Reviewers still need the full study inputs or a justified explanation of access restrictions to assess reproducibility.

## 4. Validate the release

```powershell
python scripts/check_repository.py
python scripts/make_synthetic_mapping_example.py
```

These commands check syntax and the workbook header, and generate the example input. Run training and mapping in the scientific environment described in `README.md`, inspect the results, and capture the environment using `python -m pip freeze > requirements-lock.txt`. Compare metrics and rasters with the manuscript and review `docs/REPRODUCIBILITY.md`. Passing CI does not establish model accuracy.

## 5. Create the repository and upload source code

Complete metadata, licensing, data permissions and result verification first. Create a new, empty GitHub repository; do not initialize another README or license online because these files already exist locally. Choose the official repository name, for example `PMmax`. Run these commands individually from the repository root:

```powershell
git init -b main
git add .
git status --short
git diff --cached --stat
```

Review the staged files. They should include the example inputs and scientific outputs, with large files represented by Git LFS pointers. Exclude Python caches, local environments and private configuration. After review, continue with the actual repository URL in place of the example:

```powershell
git commit -m "Prepare PMmax research software release"
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY.git
git push -u origin main
```

If using GitHub Desktop, add the directory as a local repository, review Changes, then commit and publish. Do not upload the entire directory while bypassing `.gitignore`.

## 6. Identify the version used in the manuscript

After validating the release, choose a version such as `v1.0.0`, update CHANGELOG and CITATION, and commit those changes. Tag the exact commit corresponding to the verified results:

```powershell
git tag -a v1.0.0 -m "Research software release associated with the manuscript"
git push origin v1.0.0
```

Create a GitHub Release from the tag. Describe changes, the validated environment, limitations and links to archived data and models. Archive the release with a DOI-supporting service if desired; add the DOI only after it has been assigned. Include the repository URL and specific release or DOI in the manuscript. Test a fresh clone in another directory to verify that a new user can follow the instructions.

## 7. Code and data availability statement

Replace all bracketed fields before inserting this statement into the manuscript:

> The PMmax source code, installation instructions, and usage documentation are available at [REPOSITORY URL], release [VERSION], commit [COMMIT]. The archived software release is available at [SOFTWARE DOI, IF ASSIGNED]. The input data and trained models used to produce the reported results are available at [DATA/MODEL DOI OR URL] under [APPLICABLE TERMS]. The computational environment and reproduction procedure are documented in the repository.

Use the data/model availability sentence only if those materials have actually been deposited. Otherwise, describe the restrictions and access procedure accurately.

## 8. Check journal requirements

[Elsevier's journal information](https://shop.elsevier.com/journals/computers-and-geosciences/0098-3004) calls for a public repository, clear license, English README, dependency and computational-resource documentation, usage guidance, and reproducibility materials or justified data limitations. Code comments should be in English. [CAGEO's instructions](https://github.com/cageo/author_instructions) also request the paper title, authors and code/data description. Check the current requirements when submitting and follow the handling editor's instructions. Repository preparation alone does not guarantee acceptance.

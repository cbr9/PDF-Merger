# PDF-Utils
Simple program I made for myself, written in Python and Qt5 to merge several PDFs and extract pages. The OK button still requires some tweaking. I'm also planning to rewrite everything in Go to optimize performance and avoid some PyDF2 issues.


# Options:

There are two options, mainly "merge" and "extract pages". The first only works when you select two or more documents, and it merges them in the order they were selected
(I plan to change the working to allow changing the order). The latter is only available when you select ONE document. You can select complex ranges. E.g.:
"1, 2, 3, 4, 5-7, 10-30-2" -> This would extract pages 1, 2, 3, 4, then from page 5 to 7 and then from page 10 to page 30 selecting every two pages.


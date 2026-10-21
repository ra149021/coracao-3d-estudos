// Compatibility for saved bookmarks; never load the retired case interface or data.
const source = new URLSearchParams(location.search);
const target = new URL('exercises.html', location.href);
for (const key of ['system', 'chapter']) {
  if (source.has(key)) target.searchParams.set(key, source.get(key));
}
document.getElementById('exercise-redirect').href = target.href;
location.replace(target.href);

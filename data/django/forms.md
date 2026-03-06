# Forms Traps

- `form.cleaned_data` only after `is_valid()` — raises KeyError before
- `form.save(commit=False)` — must call `save_m2m()` for ManyToMany
- `{% csrf_token %}` required in POST forms — 403 without it
- `request.FILES` needs `enctype="multipart/form-data"` — empty dict otherwise
- `ModelForm` excludes auto fields — `auto_now` not in form, can't override
- `clean_<field>()` must return value — None clears the field
- Form `__init__` must call `super().__init__(**kwargs)` first — or fields undefined
- `initial` vs `instance.field` — initial doesn't save, just displays

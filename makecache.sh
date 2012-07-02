if [[ -d pkg-cache ]]; then rm -Rf pkg-cache; fi
mkdir pkg-cache
cd pkg-cache
wget http://pypi.python.org/packages/source/D/Django/Django-1.4.tar.gz
wget http://pypi.python.org/packages/source/z/zc.recipe.egg/zc.recipe.egg-1.3.2.tar.gz
wget http://pypi.python.org/packages/source/d/django-gravatar2/django-gravatar2-1.0.4.tar.gz
wget http://pypi.python.org/packages/source/S/South/South-0.7.5.tar.gz
cd ..

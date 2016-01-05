version=`grep "Version: " control | sed '$s/Version: //g'`
package=`grep "Package: " control | sed '$s/Package: //g'`
architecture=`grep "Architecture: " control | sed '$s/Architecture: //g'`
package_name=$package"_"$version"_"$architecture
mkdir -p $package_name/DEBIAN
mkdir -p $package_name/usr/lib/python3/dist-packages/lios/
git pull
cp -r lios/* $package_name/usr/lib/python3/dist-packages/lios/
cp -r share $package_name/usr/
cp -r bin $package_name/usr/
printf "See commits : https://gitlab.com/Nalin-x-Linux/lios-3/commits/master\n\n" > $package_name/usr/share/doc/lios/changelog
git log >> $package_name/usr/share/doc/lios/changelog
gzip -9 $package_name/usr/share/doc/lios/changelog $package_name/usr/share/doc/lios/changelog.gz
cp control postinst postrm $package_name/DEBIAN/
cd $package_name
find -name "*~" -delete
find . -type f ! -regex '.*.hg.*' ! -regex '.*?debian-binary.*' ! -regex '.*?DEBIAN.*' -printf '%P ' | xargs md5sum > DEBIAN/md5sums
sudo chown -R root DEBIAN/postinst DEBIAN/postrm DEBIAN/md5sums usr/
sudo chgrp -R root DEBIAN/postinst DEBIAN/postrm DEBIAN/md5sums usr/
sudo chmod -R 0755 DEBIAN/postinst DEBIAN/postrm usr/
sudo chmod -R 0644 DEBIAN/md5sums usr/share/applications/Lios.desktop usr/share/doc/lios/* usr/share/menu/lios usr/share/man/man1/lios.1.gz
sudo chmod -R 0644 usr/share/lios/lios usr/share/lios/readme usr/share/pixmaps/lios.xpm
cd ../
dpkg -b $package_name
sudo rm -rf $package_name

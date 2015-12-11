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
cp control postinst prerm $package_name/DEBIAN/
cd $package_name
find -name "*~" -delete
find . -type f ! -regex '.*.hg.*' ! -regex '.*?debian-binary.*' ! -regex '.*?DEBIAN.*' -printf '%P ' | xargs md5sum > DEBIAN/md5sums
sudo chown -R root DEBIAN/postinst DEBIAN/prerm DEBIAN/md5sums usr/
sudo chgrp -R root DEBIAN/postinst DEBIAN/prerm DEBIAN/md5sums usr/
sudo chmod 0755 DEBIAN/postinst DEBIAN/prerm usr/
sudo chmod 0644 DEBIAN/md5sums
cd ../
dpkg -b $package_name
sudo rm -rf $package_name

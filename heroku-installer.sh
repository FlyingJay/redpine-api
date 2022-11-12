##
## (◣_(◣_(◣_◢)_◢)_◢)
## So dis file is used 
## by CI process to 
## get dat heroah ku
## installer'd so we 
## can duz deploy
## (◣_(◣_(◣_◢)_◢)_◢)
##
## thx bye.
##

HEROKU_CLIENT_URL="http://assets.heroku.com.s3.amazonaws.com/heroku-client/heroku-client.tgz"

su -c "sh <<SCRIPT
  # download and extract the client tarball
  rm -rf /usr/local/heroku
  mkdir -p /usr/local/heroku
  cd /usr/local/heroku
  if [[ -z "$(which wget)" ]]; then
    curl -s $HEROKU_CLIENT_URL | tar xz
  else
    wget -qO- $HEROKU_CLIENT_URL | tar xz
  fi
  mv heroku-client/* .
  rmdir heroku-client
  ln -sfn /usr/local/heroku/bin/heroku /usr/bin/
SCRIPT"

echo "Installation complete"%
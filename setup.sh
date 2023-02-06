sudo pip3 install -r requirements.txt
sudo cp agents_diagnostics.conf /etc/supervisor/conf.d/
sudo cp agents_diagnostics_nginx.conf /etc/nginx/sites-enabled/
sudo supervisorctl update
sudo systemctl restart nginx
sudo certbot --nginx -d diagnostics.ai.medsenger.ru

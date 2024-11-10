Rails.application.config.after_initialize do
  ActiveStorage::Current.url_options = { protocol: 'https', host: 'media-wise-api.kovalev.team', port: 443 }
end
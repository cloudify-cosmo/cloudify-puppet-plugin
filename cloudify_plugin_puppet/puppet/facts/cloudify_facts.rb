# Based on
# https://raw.githubusercontent.com/CloudifySource/cloudify-recipes/master/services/puppet/custom_facts/cloudify_facts.rb

#Load cloudify attributes into puppet
require 'json'

env_var = 'CLOUDIFY_FACTS_FILE'

if not ENV.has_key?(env_var) then
  raise "Environment variable #{env_var} is not set"
end

attributes = JSON.parse(IO.read(ENV[env_var]))

class Hash
    def flatten_to_hash(current_prefix="", separator="_")
        {}.tap do |hash|
            self.each do |key, value|
                if value.is_a?(Hash)
                    hash.merge!(value.flatten_to_hash(
                                    "#{current_prefix}#{key}#{separator}",
                                    separator))
                else
                    hash["#{current_prefix}#{key}"] = value
                end
            end
        end
    end
end

attributes.flatten_to_hash.each do |key, value|
  Facter.add(key) do
    setcode do
      value.to_s
    end
  end
end


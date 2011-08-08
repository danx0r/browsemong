query = function(args){
    db = connect("localhost/mong");
    var person = db.Person.findOne({NameRaw: args.name})
    if (!person) {
        return([])
    }
    var authors = db.Letter.find({Author: person._id}).toArray();
    var recips = db.Letter.find({Recipient: person._id}).toArray();
    return authors.concat(recips);
}

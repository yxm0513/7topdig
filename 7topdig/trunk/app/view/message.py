# -*- coding: utf-8 -*-
from flask import Blueprint, abort, jsonify, request, \
    url_for, redirect, flash, render_template
from flaskext.login import current_user
from app.lib.permissions import auth


from app.models import User, Message
from app.forms import NewMessageForm,ReplyMessageForm


mod = Blueprint('message', __name__)


@mod.route('/inbox', methods = ['GET'])
@auth.require(401)
def inbox():
    if request.method == "GET":
        messages = Message.query.recive_by(current_user).own_by(current_user).latest_order().all()
        unread = Message.query.recive_by(current_user).own_by(current_user).read(False).latest_order().all()

        d = {
            'messages': messages,
            'user': current_user,
            'unread': len(unread)
        }
        return render_template( 'message/inbox.html', **d )


@mod.route('/outbox', methods=['GET'])
@auth.require(401)
def outbox():
    if request.method == "GET":
        messages = Message.query.own_by(current_user).send_by(current_user).latest_order().all()
        return render_template( 'message/outbox.html', messages=messages, user = current_user )

@mod.route("/<int:message_id>/", methods = ['GET'])
@auth.require(401)
def view(message_id):
    if request.method == "GET":
        message = Message.query.get_or_404(message_id)
        if not message:
            flash(u"没发现消息")
            return redirect(url_for('message.inbox'))
        if message.owner_id != current_user.id:
            flash(u"你没有权限查看该消息")
            return redirect(url_for('message.inbox'))

        d = { 
             'message': message, 
             'user': current_user 
             }
        if message.read == False:
            message.read = True
            message.save()

        return render_template('message/view.html', **d)


@mod.route("/send", methods = ['GET', 'POST'])
@auth.require(401)
def send():
    if request.method == "GET":
        user_id = request.args.get('user_id')
        if user_id:
            sendto = User.query.get(user_id)
            form = NewMessageForm(sendto = sendto.username)
        else:
            form = NewMessageForm()
            #form.sendto.errors.append( u'没有这个用户') 

    if request.method == "POST":
        form = NewMessageForm()
        if form.validate_on_submit():
            # convert username to user id
            you = User.query.filter_by(username=form.sendto.data).first()

            if you and you.id != current_user.id:
                # one for sender outobx
                m1 = Message( owner = current_user, sender = current_user,
                              receiver = you,
                              subject = form.subject.data,
                              content = form.content.data)
                m1.save()

                # another one for receiver inbox
                m2 = Message( owner = you, sender = current_user,
                              receiver = you,
                              subject = form.subject.data,
                              content = form.content.data)
                m2.save()
                #
                return redirect(url_for('message.outbox'))
            else:
                if not you:
                    form.sendto.errors.append( u'没有这个用户') 
                else:
                    form.sendto.errors.append( u'你不能给自己发信息')
            # end if

    return render_template( 'message/send.html', 
                            title = u'发送信息', form = form,
                            user = current_user )


@mod.route("/<int:message_id>/delete/", methods = ['POST'])
@auth.require(401)
def delete(message_id):

        message = Message.query.get_or_404(message_id)
        if not message:
            flash(u"未发现信息")
            return jsonify(success=False, redirect_url=url_for('message.outbox'))

        if not message.read:
            flash(u"未读信息")

        message.delete()
        flash(u'成功删除消息.', 'successfully')  
        return jsonify(success=True, redirect_url=url_for('message.outbox'))


@mod.route("/<int:message_id>/reply", methods = ['GET', 'POST'])
@auth.require(401)
def reply(message_id):
    message = Message.query.get_or_404(message_id)
    if not message:
        flash(u"未发现信息: %s" % id)
        return redirect(url_for('message.inbox'))

    if message.owner_id != current_user.id:
        flash(u"你没有权限回复该消息")
        return redirect(url_for('message.inbox'))

    if request.method == "GET":

        # compose repily message content
        reply = "\n".join(map(lambda line:"> "+line, message.content.split("\n")))

        content = "在 %s, %s 写:\n%s" %(message.dateshow, message.sender.username, reply)
        form = ReplyMessageForm(subject="Re:"+message.subject, content=content)

    if request.method == "POST":

        form = ReplyMessageForm()
        if form.validate_on_submit():
            m1 = Message( owner = message.receiver, sender = message.receiver, 
                          receiver = message.sender, 
                          subject = form.subject.data,
                          content = form.content.data)
            m1.save()

            m2= Message( owner = message.sender, sender = message.receiver, 
                          receiver = message.sender, 
                          subject = form.subject.data,
                          content = form.content.data)
            m2.save()

            url = url_for('message.outbox')
            return redirect(url)

    return render_template( 'message/reply.html', tilte = u'回复信息', 
                            message = message, form = form, user = current_user)

@mod.route('/unreadnum', methods = ['GET'])
@auth.require(401)
def unreadnum():
    num = Message.query.recive_by(current_user).own_by(current_user).read(False).latest_order().all()
    return jsonify(num=len(num))